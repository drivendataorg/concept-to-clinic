<template>
  <vue-draggable-resizable class="nodule-marker" :class="{ overlapped: markerOverlappedBySlice }"
                           v-if="dynamicMarker" :x="dynamicMarker.x" :y="dynamicMarker.y"
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
      translation: null,
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
          this.resetDynamicMarker(newMarker)
        } else {
          this.dynamicMarker = this.scaleMarker(newMarker)
        }
      },
      translation () {
        this.resetDynamicMarker(this.marker)
      }
    },
    computed: {
      markerOverlappedBySlice () {
        const val = this.dynamicMarker.z !== this.sliceIndex
        return val
      }
    },
    methods: {
      resetDynamicMarker (marker) {
        // destroy
        this.dynamicMarker = null

        // reinit
        var self = this
        Vue.nextTick(function () {
          self.dynamicMarker = self.scaleMarker(marker)
        })
      },
      scaleMarker (marker) {
        if (!marker) {
          return null
        }

        let scaledInfo = { ...marker }

        if (this.translation) {
          // scale the position and add the offset
          // the size of marker is subtracted to move the image center to target position
          scaledInfo.x = marker.x * this.translation.scale + this.translation.offsetX - this.markerImageSize / 2
          scaledInfo.y = marker.y * this.translation.scale + this.translation.offsetY - this.markerImageSize / 2
        }

        return scaledInfo
      },
      onDragFinished (x, y) {
        // reverting the transformation
        const scaled = this.translation
            ? {
              x: Math.round((x + this.markerImageSize / 2 - this.translation.offsetX) / this.translation.scale),
              y: Math.round((y + this.markerImageSize / 2 - this.translation.offsetY) / this.translation.scale)
            }
            : { x, y }

        EventBus.$emit('nodule-marker-moved', scaled.x, scaled.y, this.sliceIndex)
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
