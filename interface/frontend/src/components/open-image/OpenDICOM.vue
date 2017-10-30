<template>
  <div class="DICOM-container">
    <div class="DICOM-description">{{ display }}</div>
    <div class="DICOM" ref="DICOM"></div>
  </div>
</template>

<script>
  const cornerstone = require('cornerstone-core')

  export default {
    name: 'open-dicom',
    props: {
      view: {
        type: Object,
        default: {
          type: 'DICOM',
          prefixCS: ':/',
          prefixUrl: null,
          path: null
        }
      }
    },
    data () {
      return {
        base64data: null
      }
    },
    computed: {
      async info () {
        const response = await this.$axios.get(this.view.prefixUrl + this.view.path)
        return response.data
      },
      async dicom () {
        const info = await this.info
        this.base64data = info.image
        return {
          imageId: this.view.type + this.view.prefixCS + this.view.path,
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
      },
      async display () {
        const element = this.$refs.DICOM
        const dicom = await this.dicom
        this.initCS(element)

        cornerstone.registerImageLoader(this.view.type, () => {
          return new Promise((resolve) => { resolve(dicom) })
        })
        const image = await cornerstone.loadImage(dicom.imageId)
        cornerstone.displayImage(element, image)
        return image
      }
    },
    methods: {
      initCS (element) {
        try {
          cornerstone.getEnabledElement(element)
        } catch (e) {
          cornerstone.enable(element)
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
