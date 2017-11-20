<template>
  <div class="DICOM-container">
    <div class="DICOM-description">{{ display }}</div>
    <div class="DICOM" ref="DICOM"></div>
    <nodule-marker :marker="marker" :zoomRate="zoomRate" :offsetX="offsetX" :offsetY="offsetY"></nodule-marker>
  </div>
</template>

<script>
  import NoduleMarker from './NoduleMarker'

  const cornerstone = require('cornerstone-core')
  const cornerstoneTools = require('cornerstone-tools')
  const jquery = require('jquery-slim')
  const _ = require('lodash')
  cornerstoneTools.external.cornerstone = cornerstone
  cornerstoneTools.external.$ = jquery

  export default {
    components: {NoduleMarker},
    name: 'open-dicom',
    props: {
      view: {
        type: Object,
        default: {
          type: 'DICOM',
          prefixCS: ':/',
          prefixUrl: null,
          paths: []
        }
      },
      // a marker that indicates the nodule centroid location ({ x, y, z })
      marker: null
    },
    data () {
      return {
        stack: {
          currentImageIdIndex: 0,
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
      'view.paths': function (val) {
        const element = this.$refs.DICOM
        this.pool = []
        this.stack.currentImageIdIndex = 0
        this.stack.imageIds = this.view.paths.map((path) => {
          return this.view.type + this.view.prefixCS + path
        }, this)
        cornerstone.disable(element)
        this.initCS(element)
      }
    },
    computed: {
      async info () {
        if (this.pool.length <= this.stack.currentImageIdIndex) {
          const hola = await this.$axios.get(this.view.prefixUrl + this.view.paths[this.stack.currentImageIdIndex])
          this.pool.push(hola)
        }
        return this.pool[this.stack.currentImageIdIndex]
      },
      async dicom () {
        let info = await this.info
        info = info.data
        if (!info) return {}
        else {
          this.base64data = info.image
          return {
            imageId: this.stack.imageIds[this.stack.currentImageIdIndex],
            slope: info.metadata['Rescale Slope'],
            rows: info.metadata['Rows'],
            columns: info.metadata['Columns'],
            height: info.metadata['Rows'],
            width: info.metadata['Columns'],
            columnPixelSpacing: info.metadata['Pixel Spacing']['0'],
            rowPixelSpacing: info.metadata['Pixel Spacing']['1'],
            sizeInBytes: info.metadata['Rows'] * info.metadata['Columns'] * 2,
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
        if (_.isEmpty(dicom)) return ''
        else {
          cornerstone.registerImageLoader(this.view.type, () => {
            return new Promise((resolve) => { resolve(dicom) })
          })
          const image = await cornerstone.loadImage(dicom.imageId)
          cornerstone.displayImage(element, image)
          return image
        }
      }
    },
    methods: {
      initCS (element) {
        try {
          cornerstone.getEnabledElement(element)
        } catch (e) {
          cornerstone.enable(element)
          cornerstoneTools.mouseInput.enable(element)
          cornerstoneTools.addStackStateManager(element, ['stack'])
          cornerstoneTools.addToolState(element, 'stack', this.stack)
          cornerstoneTools.stackScroll.activate(element, 1)
          cornerstoneTools.stackScrollWheel.activate(element)
          cornerstoneTools.scrollIndicator.enable(element)
          cornerstoneTools.wwwc.activate(element, 1)
        }
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
