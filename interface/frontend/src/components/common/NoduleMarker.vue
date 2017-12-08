<template>
  <vue-draggable-resizable class="nodule-marker" :class="{ overlapped: markerOverlappedBySlice }"
                           v-if="scaledMarker" :x="scaledMarker.x" :y="scaledMarker.y"
                           :w="markerImageSize" :h="markerImageSize"
                           :minw="markerImageSize" :minh="markerImageSize"
                           :resizable="false" v-on:dragstop="onDragFinished">
  </vue-draggable-resizable>
</template>

<script>
  import Vue from 'vue'
  import VueDraggableResizable from 'vue-draggable-resizable'
  import {EventBus} from '../../main.js'

  export default {
    components: {VueDraggableResizable},
    name: 'open-dicom',
    props: {
      zoomRate: null,
      offsetX: null,
      offsetY: null,
      marker: null,
      sliceIndex: {
        type: Number
      }
    },
    data () {
      const markerImageSize = 32
      return {
        markerImageSize: markerImageSize,
        // TODO: can be removed as soon as 'vue-draggable-resizable' will support coordinates update
        dynamicMarker: this.marker
      }
    },
    watch: {
      // TODO: remove this watcher as soon as this issue is closed https://github.com/mauricius/vue-draggable-resizable/issues/14
      marker: function (newMarker, oldMarker) {
        // if both new and old marker defined we've got a problem:
        // component will not detect coordinates update, so let's destroy and reinit it
        if (newMarker && oldMarker) {
          // destroy
          this.dynamicMarker = null

          // reinit
          var self = this
          Vue.nextTick(function () {
            self.dynamicMarker = newMarker
          })
        } else {
          this.dynamicMarker = newMarker
        }
      }
    },
    computed: {
      scaledMarker () {
        if (!this.dynamicMarker) {
          return null
        }

        var scaledInfo = {x: this.dynamicMarker.x, y: this.dynamicMarker.y, z: this.dynamicMarker.z}

        // converting from true DICOM pixels to display pixels
        scaledInfo.x = scaledInfo.x * this.zoomRate - this.offsetX - this.markerImageSize / 2
        scaledInfo.y = scaledInfo.y * this.zoomRate - this.offsetY - this.markerImageSize / 2

        return scaledInfo
      },
      markerOverlappedBySlice () {
        const val = this.scaledMarker.z !== this.sliceIndex
        return val
      }
    },
    methods: {
      onDragFinished (x, y) {
        var scaledX = x / this.zoomRate + this.offsetX + this.markerImageSize / 2
        var scaledY = y / this.zoomRate + this.offsetY + this.markerImageSize / 2

        EventBus.$emit('nodule-marker-moved', scaledX, scaledY, this.sliceIndex)
      }
    }
  }
</script>

<style lang="scss" scoped>
  @keyframes opacity-pulse {
    0% { opacity: 0.3; }
    50% { opacity: 0.9; }
    100% { opacity: 0.3; }
  }

  .DICOM-container {
    .nodule-marker {
      background-image: url('../../assets/images/nodule-marker.png');

      &.overlapped {
        animation: opacity-pulse 1s infinite ease-in-out;
      }
    }
  }
</style>
