<template>
  <ul>
    <li>
      <span @click="toggle" v-if="isOpenable">
        {{ model.name }} [{{open ? '-' : '+'}}]
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
        ></tree-view>
        <li @click="select()" v-for="file in model.files" class="text-muted" :key="file.name">{{ file.name }}</li>
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
      }
    },
    methods: {
      toggle: function () {
        this.$set(this, 'open', !this.open)
      },
      select: function () {
        EventBus.$emit('dicom-selection', this.model.files.map((file) => { return file.path }))
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
