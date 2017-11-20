<template>
<div id="app">
  <app-nav></app-nav>
  <router-view></router-view>
</div>
</template>

<script>
import AppNav from './components/AppNav'

export default {
  components: {
    AppNav
  }
}
</script>

<style lang="scss" scoped>
.container {
  margin-top: 72px;
  a {
    color: red;
  }
}

</style>

<style media="screen">
  .offset-top {
    margin-top: 5em;
  }

  @media screen and (max-width: 990px) {
    .offset-top {
      margin-top: 10em;
    }
  }

  .cursor-pointer {
    cursor: pointer;
  }
</style>
