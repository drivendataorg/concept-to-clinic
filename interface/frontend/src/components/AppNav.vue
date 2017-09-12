<template>
<nav class="navbar navbar-toggleable-md navbar-inverse bg-inverse fixed-top">
  <img src="../assets/images/c-logo-light.svg"/>
  <a class="navbar-brand" href="#">Concept To Clinic</a>
  <div class="navbar-collapse collapse" id="navbar">
    <ul class="navbar-nav justify-content-center">
      <li class="nav-item active">
        <a class="nav-link" href="#">Open image</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="#">Detect and Select</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="#">Annotate and Segment</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="#">Report and Export</a>
      </li>
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
