<template>
  <canvas ref="canvas" @contextmenu="onRightClick" @mousedown="onMouseDown" @mousemove="onMouseMove"
          @mouseup="onMouseUp" :width="canvasWidth" :height="canvasHeight" :style="canvasStyle">
  </canvas>
</template>

<script>
  // how close near the point should user click to grasp it
  const graspSensitivity = 6

  // selected area style
  const strokePolygonRgb = 'rgb(255,255,255)'
  const fillPolygonRgba = 'rgba(255, 255, 90, 0.2)'

  // point style
  const strokeCoordRgb = 'rgb(255, 255, 90)'
  const fillCoordRgb = 'rgb(255, 255, 90)'

  export default {
    components: {},
    props: ['width', 'height', 'selectedArea'],
    data () {
      return {
        areaCoordinates: this.selectedArea || [],
        draggingPointIndex: -1,
        lastMouseLocation: null,
        draggingEntireArea: false,
        canvasWidth: this.width || 512,
        canvasHeight: this.height || 512,
        anyMovesDetected: false
      }
    },
    watch: {
      areaCoordinates () {
        this.redrawAndNotify()
      }
    },
    created () {
    },
    mounted: function () {
      this.canvas = this.$refs['canvas']

      if (!this.canvas.getContext) {
        // IE Support
        // eslint-disable-next-line no-undef
        this.canvas = G_vmlCanvasManager.initElement(this.canvas)
      }

      this.canvasContext = this.canvas.getContext('2d')
      this.redraw()
    },
    computed: {
      canvasStyle () {
        return {
          width: this.canvasWidth + 'px',
          height: this.canvasHeight + 'px',
          position: 'absolute',
          top: 0,
          left: 0
        }
      }
    },
    methods: {
      onRightClick (e) {
        this.preventDefault(e)

        const {x, y} = this.getMouseLocation(e)

        for (let [i, pointLocation] of this.areaCoordinates.entries()) {
          let dis = Math.sqrt(Math.pow(x - pointLocation[0], 2) + Math.pow(y - pointLocation[1], 2))
          if (dis < graspSensitivity) {
            this.areaCoordinates.splice(i, 1)
            return false
          }
        }

        return false
      },
      onMouseDown (e) {
        let coords = this.areaCoordinates

        // right mouse button click
        if (e.which === 3) {
          return false
        }

        const {x, y} = this.getMouseLocation(e)
        this.lastMouseLocation = {x, y}

        if (e.shiftKey) {
          this.draggingEntireArea = true
          return
        }

        // move existing point
        for (let [i, pointLocation] of coords.entries()) {
          let dis = Math.sqrt(Math.pow(x - pointLocation[0], 2) + Math.pow(y - pointLocation[1], 2))
          if (dis < graspSensitivity) {
            this.draggingPointIndex = i
            return false
          }
        }

        // looking for two nearest neighbour points
        const coordsCopy = coords.slice(0)

        // adding first item for checking last-first pair
        coordsCopy.push(coordsCopy[0])

        const lines = coordsCopy.map((pointLocation, i) => {
          if (i === 0) {
            return {index: 0, distance: Number.MAX_SAFE_INTEGER}
          }

          // make a line from current and previous point, and check click is close
          let lineDistance = this.pointToLineLength(
              x, y,
              pointLocation[0], pointLocation[1],
              coordsCopy[i - 1][0], coordsCopy[i - 1][1],
              true
          )

          return {index: i, distance: lineDistance}
        })

        // find the two nearest neighbour points
        const closestLine = lines.sort((l1, l2) => l1.distance - l2.distance)[0]

        // insert new point
        coords.splice(closestLine.index, 0, [x, y])

        // set currently dragging point
        this.draggingPointIndex = closestLine.index

        return false
      },
      onMouseMove (e) {
        const lastLocation = this.lastMouseLocation
        const {x, y} = this.getMouseLocation(e)
        this.lastMouseLocation = {x, y}

        const dX = x - lastLocation.x
        const dY = y - lastLocation.y

        if (Math.abs(dX) < 1 && Math.abs(dY) < 1) {
          return
        }

        if (this.draggingPointIndex >= 0) {
          // if we have an active point - drag it

          this.areaCoordinates[this.draggingPointIndex][0] = Math.round(x)
          this.areaCoordinates[this.draggingPointIndex][1] = Math.round(y)
        } else if (this.draggingEntireArea && lastLocation) {
          // if entire area is being dragged - update all points

          for (let pointLocation of this.areaCoordinates) {
            pointLocation[0] += dX
            pointLocation[1] += dY
          }
        } else {
          return
        }

        this.anyMovesDetected = true
        this.redraw()
      },
      onMouseUp (e) {
        if (this.draggingPointIndex < 0 && !this.draggingEntireArea) {
          return
        }

        if (this.anyMovesDetected) {
          this.notify()
        }

        this.draggingPointIndex = -1
        this.draggingEntireArea = false
        this.anyMovesDetected = false
      },
      redrawAndNotify () {
        this.redraw()
        this.notify()
      },
      notify () {
        this.$emit('selection-changed', this.areaCoordinates)
      },
      redraw () {
        this.canvasContext.clearRect(0, 0, this.canvas.width, this.canvas.height)
        this.canvasContext.globalCompositeOperation = 'source-over'
        this.drawArea()
      },
      drawArea () {
        let coords = this.areaCoordinates

        if (coords.length < 1) {
          return false
        }

        this.canvasContext.lineWidth = 1

        // draw polygon
        this.canvasContext.beginPath()
        this.canvasContext.moveTo(coords[0][0], coords[0][1])

        for (let pointLocation of coords) {
          this.canvasContext.lineTo(pointLocation[0], pointLocation[1])
        }

        // finish the polygon
        this.canvasContext.closePath()
        this.canvasContext.strokeStyle = strokePolygonRgb
        this.canvasContext.stroke()
        this.canvasContext.fillStyle = fillPolygonRgba
        this.canvasContext.fill()

        // draw draggable points
        this.canvasContext.strokeStyle = strokeCoordRgb
        this.canvasContext.fillStyle = fillCoordRgb

        for (let pointLocation of coords) {
          this.canvasContext.beginPath()
          this.canvasContext.arc(pointLocation[0], pointLocation[1], 4, 0, 2 * Math.PI)
          this.canvasContext.fill()
        }
      },
      getElementOffset (element) {
        const de = document.documentElement
        const box = element.getBoundingClientRect()
        const top = box.top + window.pageYOffset - de.clientTop
        const left = box.left + window.pageXOffset - de.clientLeft
        return {top: top, left: left}
      },
      preventDefault (e) {
        if (e.stopPropagation) e.stopPropagation()
        if (e.preventDefault) e.preventDefault()
      },
      getMouseLocation (e) {
        const canvasOffset = this.getElementOffset(this.canvas)
        const x = (e.pageX - canvasOffset.left)
        const y = (e.pageY - canvasOffset.top)

        return {x, y}
      },
      // + Jonas Raoni Soares Silva
      // @ http://jsfromhell.com/math/dot-line-length [rev. #1]
      pointToLineLength (x, y, x0, y0, x1, y1, o) {
        /*eslint-disable */
        function lineLength (x, y, x0, y0) {
          return Math.sqrt((x -= x0) * x + (y -= y0) * y)
        }

        if (o && !(o = function (x, y, x0, y0, x1, y1) {
              if (!(x1 - x0)) return {x: x0, y: y}
              else if (!(y1 - y0)) return {x: x, y: y0}
              var left, tg = -1 / ((y1 - y0) / (x1 - x0))
              return {
                x: left = (x1 * (x * tg - y + y0) + x0 * (x * -tg + y - y1)) / (tg * (x1 - x0) + y0 - y1),
                y: tg * left - tg * x + y
              }
            }(x, y, x0, y0, x1, y1), o.x >= Math.min(x0, x1) && o.x <= Math.max(x0, x1) && o.y >= Math.min(y0, y1) && o.y <= Math.max(y0, y1))) {
          var l1 = lineLength(x, y, x0, y0), l2 = lineLength(x, y, x1, y1)
          return l1 > l2 ? l2 : l1
        }
        else {
          var a = y0 - y1, b = x1 - x0, c = x0 * y1 - y0 * x1
          return Math.abs(a * x + b * y + c) / Math.sqrt(a * a + b * b)
        }
        /*eslint-enable */
      }
    }
  }
</script>
