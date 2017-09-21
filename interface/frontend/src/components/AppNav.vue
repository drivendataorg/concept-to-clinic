<template>
<nav class="navbar navbar-toggleable-md navbar-inverse bg-inverse fixed-top">
  <img src="../assets/images/c-logo-light.svg"/>
  <a class="navbar-brand" href="#">Concept To Clinic</a>
  <div class="navbar-collapse collapse" id="navbar">
    <ul class="navbar-nav justify-content-center">
      <router-link to="/" tag="li" class="nav-item" exact>
        <a class="nav-link">Open Image</a>
      </router-link>
      <router-link to="/detect-and-select" tag="li" class="nav-item">
        <a class="nav-link">Detect and Select</a>
      </router-link>
      <router-link to="/annotate-and-segment" tag="li" class="nav-item">
        <a class="nav-link">Annotate and Segment</a>
      </router-link>
      <router-link to="/report-and-export" tag="li" class="nav-item">
        <a class="nav-link">Report and Export</a>
      </router-link>
    </ul>
  </div>
  <span class="navbar-text">
    {{ appVersion }}
  </span>
</nav>
</template>

<script>
export default {
  data () {
    return {
      appVersion: 'a0b1c2d'
    }
  }
}
</script>

<style>
.navbar > img {
  height: 20px;
  padding: 2px;
  width: auto;
}
</style>
