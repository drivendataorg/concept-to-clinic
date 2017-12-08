<template>
  <ul>
    <li>
      <span @click="toggle(model)" v-if="isOpenable">
        [{{open ? '-' : '+'}}] <span :style="selectedStyle">{{ model.name }}</span>
      </span>
      <span v-else>
        {{ model.name }}
      </span>
      <span class="badge badge-default" v-if="hasFiles">
        {{ model.files.length }}
      </span>
      <ul v-show="isOpen" v-if="isFolder">
        <tree-view class="item"
                   v-for="child in model.children"
                   v-if="child.children"
                   :key="child.name"
                   :model="child"
                   :selectedSeries="selectedSeries"
                   :parent="parent + '/' + model.name"
                   v-on:childSelected="selectSeries"
                   v-on:selectSeries="selectSeries"
        ></tree-view>
        <li @click="select(file)" v-for="file in model.files" class="text-muted" :key="file.name">{{ file.name }}</li>
      </ul>
    </li>
  </ul>
</template>

<script>
  import TreeView from './TreeView'
  import { EventBus } from '../../main.js'

  export default {
    name: 'tree-view',
    props: {
      parent: '',
      selectedSeries: null,
      model: {
        type: Object,
        default: {
          'name': 'root',
          'children': [],
          'files': [],
          'type': 'folder'
        }
      }
    },
    components: {
      TreeView
    },
    data () {
      return {
        open: false
      }
    },
    computed: {
      isFolder () {
        return this.model.type === 'folder'
      },
      hasContents () {
        return this.hasFiles || this.hasFolders
      },
      hasFolders () {
        if (this.model.children) return this.model.children.length > 0
        return false
      },
      hasFiles () {
        if (this.model.files) return this.model.files.length > 0
        return false
      },
      isOpenable () {
        return this.isFolder && this.hasContents
      },
      isOpen () {
        return this.open
      },
      selectedStyle () {
        if (this.selectedSeries && this.selectedSeries.indexOf(this.model.name) !== -1) {
          return { 'text-decoration': 'underline' }
        }
        //   return {}
        // }
        return {}
      },
      fullPath () {
        return this.parent + '/' + this.model.name
      }
    },
    methods: {
      toggle: function (model) {
        this.$set(this, 'open', !this.open)
      },
      selectSeries: function (seriesId) {
        this.$emit('selectSeries', seriesId)
      },
      select: function (file) {
        // file selected should tell parent series
        this.$emit('childSelected', this.fullPath)

        EventBus.$emit('dicom-selection',
          {
            paths: this.model.files.map((file) => { return file.path }),
            state: file.path
          })
      }
    }
  }
</script>

<style lang="scss" scoped>
  .item {
    cursor: pointer;
  }

  .bold {
    font-weight: bold;
  }

  ul {
    padding-left: 1em;
    line-height: 1.5em;
    list-style-type: dot;
  }
</style>
