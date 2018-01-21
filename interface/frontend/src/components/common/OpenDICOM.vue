<template>
  <div class="DICOM-container">
    <div class="DICOM-description">{{ display }}</div>
    <div class="DICOM-toolbar" v-if="view.paths.length">
      <div v-if="showAreaSelect">
        <label class="checkbox-inline"><input type="checkbox" v-model="imageNavigationEnabled">
          Image Navigation
        </label>
      </div>
      <input
        class="DICOM-range"
        type="range"
        min="0"
        v-bind:max="view.paths.length - 1"
        v-bind:value="stack.currentImageIdIndex"
        v-on:input="rangeSlice($event)"
      >
      slice index: <b>{{ stack.currentImageIdIndex }} </b>
    </div>
    <div class="DICOM" oncontextmenu="return false" ref="DICOM"></div>
    <nodule-marker :marker="marker" :sliceIndex="stack.currentImageIdIndex"
                   :translation="translation"></nodule-marker>
    <div :class="{ 'skip-events': imageNavigationEnabled }">
      <area-select v-if="showAreaSelect" @selection-changed="scaledNoduleCoordinatesChanged" 
                   :areaCoordinates="scaledAreaCoordinates"></area-select>
    </div>
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
      areaCoordinates: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        stack: {
          currentImageIdIndex: this.view.sliceIndex,
          imageIds: []
        },

        imageNavigationEnabled: !this.showAreaSelect,
        base64data: null,
        pool: [],
        translation: null,
        csViewport: null,
        scaledAreaCoordinates: [],
        lastCoordinates: null
      }
    },
    watch: {
      'view.sliceIndex' (newIndex) {
        this.stack.currentImageIdIndex = newIndex
      },
      'view.paths' (val) {
        this.updateViewer()
      },
      'stack.currentImageIdIndex' () {
        this.scaleCurrentAreaCoordinates()
      },
      translation () {
        this.scaleCurrentAreaCoordinates()
      },
      areaCoordinates (newCoordinates) {
        if (newCoordinates === this.lastCoordinates) {
          return
        }

        this.lastCoordinates = newCoordinates

        this.scaleCurrentAreaCoordinates()
      },
      scaledAreaCoordinates (newCoords) {
        this.scaledNoduleCoordinatesChanged(newCoords)
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
          } else {
            console.log('No path in paths for index ', this.stack.currentImageIdIndex)
          }
        }

        return this.pool[this.stack.currentImageIdIndex]
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

        if (!dicom || !element) return ''
        else {
          cornerstone.registerImageLoader(this.view.type, () => {
            return {promise: new Promise((resolve) => { resolve(dicom) })}
          })
          const image = await cornerstone.loadAndCacheImage(dicom.imageId)
          cornerstone.displayImage(element, image, this.csViewport)

          // default resize only when there is no custom zoom\pan
          if (!this.csViewport) {
            cornerstone.resize(element, true)
          }

          element.addEventListener('cornerstoneimagerendered', this.onImageRendered)

          return image
        }
      }
    },
    mounted: function () {
      this.updateViewer()
    },
    methods: {
      // scaled nodule area coordinates for current slice
      scaleCurrentAreaCoordinates () {
        const currentCoordinates = this.areaCoordinates[this.stack.currentImageIdIndex] || []

        // copy as a new object
        const scaledCoordinates = JSON.parse(JSON.stringify(currentCoordinates))

        // scale
        if (this.translation) {
          for (let point of scaledCoordinates) {
            point[0] = point[0] * this.translation.scale + this.translation.offsetX
            point[1] = point[1] * this.translation.scale + this.translation.offsetY
          }
        }

        this.scaledAreaCoordinates = scaledCoordinates
      },
      onImageRendered (e) {
        const img = cornerstone.getImage(e.target)
        const imgWidth = img.width
        const imgHeight = img.height
        const csViewport = cornerstone.getViewport(e.target)

        // cornerstone tool gives us the offset of the center of DICOM image
        // this is pretty useless for us, so we have to convert it to the offset of the top-left corner
        // top-left corner offset caused by zoom equals = - deltaWidth / 2
        // translation.x, .y gives us unscaled panning offset
        this.translation = {
          scale: csViewport.scale,
          offsetX: csViewport.translation.x * csViewport.scale - (imgWidth * csViewport.scale - imgWidth) / 2,
          offsetY: csViewport.translation.y * csViewport.scale - (imgHeight * csViewport.scale - imgHeight) / 2
        }

        // saving viewport to preserve it when navigating through slices
        this.csViewport = csViewport
      },
      scaledNoduleCoordinatesChanged (newCoords) {
        // copy as a new object
        const unscaledCoordinates = JSON.parse(JSON.stringify(newCoords))

        // unscale
        if (this.translation) {
          for (let point of unscaledCoordinates) {
            point[0] = Math.round((point[0] - this.translation.offsetX) / this.translation.scale)
            point[1] = Math.round((point[1] - this.translation.offsetY) / this.translation.scale)
          }
        }

        this.areaCoordinates.splice(this.stack.currentImageIdIndex, 1, unscaledCoordinates)
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
          cornerstoneTools.mouseWheelInput.enable(element)

          cornerstoneTools.addStackStateManager(element, ['stack'])
          cornerstoneTools.addToolState(element, 'stack', this.stack)

          cornerstoneTools.zoomWheel.activate(element) // zoom assigned to mouse wheel
          cornerstoneTools.wwwc.activate(element, 4) // ww\wc assigned to right mouse button
          cornerstoneTools.pan.activate(element, 1) // pan assigned to left mouse button
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

    .skip-events {
      pointer-events: none;
    }
  }

  .DICOM {
    width:512px;
    height:512px;
    top:0px;
    left:0px;
    position:absolute;
  }
</style>
