<template>
  <div class="DICOM-container" style="width: 100%">
    <div class="DICOM-description">{{ display }}</div>
    <div class="DICOM-toolbar" v-if="view.paths.length">
      <input
        class="DICOM-range"
        type="range"
        min="0"
        v-bind:max="view.paths.length"
        v-bind:value="stack.currentImageIdIndex"
        v-on:input="rangeSlice($event)"
      >
      slice index: <b>{{ stack.currentImageIdIndex }} </b>
    </div>
    <div class="DICOM" ref="DICOM" style="width: 100%"></div>
    <nodule-marker :marker="marker" :sliceIndex="stack.currentImageIdIndex" :zoomRate="zoomRate" :offsetX="offsetX" :offsetY="offsetY"></nodule-marker>
    <area-select @selection-changed="areaSelectChange" v-if="showAreaSelect" :areaCoordinates="areaCoordinates"></area-select>
  </div>
</template>

<script>
  import AreaSelect from './AreaSelect'
  import NoduleMarker from './NoduleMarker'

  const cornerstone = require('cornerstone-core')
  const cornerstoneTools = require('cornerstone-tools')
  const cornerstoneMath = require('cornerstone-math')

  cornerstoneTools.external.cornerstone = cornerstone
  cornerstoneTools.external.cornerstoneMath = cornerstoneMath

  export default {
    components: {AreaSelect, NoduleMarker},
    name: 'open-dicom',
    props: {
      view: {
        type: Object,
        default: {
          type: 'DICOM',
          prefixCS: ':/',
          prefixUrl: null,
          paths: [],
          state: '',
          sliceIndex: 0
        }
      },
      // a marker that indicates the nodule centroid location ({ x, y, z })
      marker: null,
      // whether to enable area selection
      showAreaSelect: false,
      areaCoordinates: []
    },
    data () {
      return {
        stack: {
          currentImageIdIndex: this.sliceIndex,
          imageIds: []
        },

        // user should be able to zoom, pan, and navigate through slices in the image viewer
        // TODO implement these features
        zoomRate: 1.0,
        offsetX: 0,
        offsetY: 0,

        base64data: null,
        pool: []
      }
    },
    watch: {
      'view.sliceIndex' (newIndex) {
        this.stack.currentImageIdIndex = newIndex
      },
      'view.paths' (val) {
        this.updateViewer()
      }
    },
    computed: {
      async info () {
        if (typeof this.pool[this.stack.currentImageIdIndex] === 'undefined') {
          // workaround for now; sometimes we have full url, sometimes filepath
          // const hola = await this.$axios.get(this.view.prefixUrl + this.view.paths[this.stack.currentImageIdIndex])
          var hola

          if (this.view.paths.length > 0 && this.view.paths.length > this.stack.currentImageIdIndex) {
            if (this.view.paths[this.stack.currentImageIdIndex].indexOf('=') !== -1) {
              hola = await this.$axios.get(this.view.paths[this.stack.currentImageIdIndex])
            } else {
              hola = await this.$axios.get(this.view.prefixUrl + this.view.paths[this.stack.currentImageIdIndex])
            }
            this.pool[this.stack.currentImageIdIndex] = hola
            return hola
          } else {
            console.log('No path in paths for index ', this.stack.currentImageIdIndex)
          }
        }
      },
      async dicom () {
        let info = await this.info
        if (!info || !info.data) return null
        else {
          info = info.data
          this.base64data = info.image
          return {
            imageId: this.stack.imageIds[this.stack.currentImageIdIndex],
            slope: info.metadata['rescale_slope'],
            rows: info.metadata['rows'],
            columns: info.metadata['columns'],
            height: info.metadata['rows'],
            width: info.metadata['columns'],
            columnPixelSpacing: info.metadata['pixel_spacing_col'],
            rowPixelSpacing: info.metadata['pixel_spacing_row'],
            sizeInBytes: info.metadata['rows'] * info.metadata['columns'] * 2,
            minPixelValue: 0,
            maxPixelValue: 255,
            intercept: 0,
            windowCenter: 110,
            windowWidth: 100,
            render: cornerstone.renderGrayscaleImage,
            getPixelData: this.getPixelData,
            color: false
          }
        }
      },
      async display () {
        const element = this.$refs.DICOM
        const dicom = await this.dicom
        if (!dicom) return ''
        else {
          cornerstone.registerImageLoader(this.view.type, () => {
            return {promise: new Promise((resolve) => { resolve(dicom) })}
          })
          const image = await cornerstone.loadAndCacheImage(dicom.imageId)

          // console.log(element)

          // cornerstone.enable(this.$refs.DICOM)
          cornerstone.displayImage(element, image)
          cornerstone.resize(element, true)
          return image
        }
      }
    },
    mounted: function () {
      this.updateViewer()
    },
    methods: {
      areaSelectChange (newCoords) {
        console.log('areaSelectChanged', JSON.stringify(newCoords))
      },
      rangeSlice (e) {
        this.stack.currentImageIdIndex = Number(e.target.value)
      },
      initCS (element) {
        try {
          cornerstone.getEnabledElement(element)
        } catch (e) {
          cornerstone.enable(element)
          cornerstoneTools.mouseInput.enable(element)
          cornerstoneTools.addStackStateManager(element, ['stack'])
          cornerstoneTools.addToolState(element, 'stack', this.stack)
          cornerstoneTools.stackScroll.activate(element, 1)
        }
      },
      updateViewer () {
        const element = this.$refs.DICOM
        this.pool = Array(this.view.paths.length)

        if (this.view.sliceIndex >= 0) {
          this.stack.currentImageIdIndex = this.view.sliceIndex
        } else {
          this.stack.currentImageIdIndex = this.view.paths.indexOf(this.view.state)
          if (this.stack.currentImageIdIndex < 0) this.stack.currentImageIdIndex = 0
        }

        this.stack.imageIds = this.view.paths.map((path) => {
          return this.view.type + this.view.prefixCS + path
        }, this)
        cornerstone.disable(element)
        this.initCS(element)
      },
      str2pixelData (str) {
        let buf = new ArrayBuffer(str.length * 2) // 2 bytes for each char
        let bufView = new Int16Array(buf)
        let index = 0
        for (let i = 0, strLen = str.length; i < strLen; i += 2) {
          bufView[index] = str.charCodeAt(i) + (str.charCodeAt(i + 1) << 8)
          index++
        }
        return bufView
      },
      getPixelData () {
        let pixelDataAsString = window.atob(this.base64data)
        let pixelData = this.str2pixelData(pixelDataAsString)
        return pixelData
      }
    }
  }
</script>

<style lang="scss" scoped>
  .DICOM-toolbar {
    position: relative;
    top: 100%;
    color: #292b2c;
  }

  .DICOM-container {
    width:512px;
    height:512px;
    position:relative;
    display:inline-block;
    color:white;
  }

  .DICOM {
    width:512px;
    height:512px;
    top:0px;
    left:0px;
    position:absolute;
  }
</style>
