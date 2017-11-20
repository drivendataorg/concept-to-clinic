<template>
  <div class="card-block">
    <table>
      <tbody>
        <tr>
          <td>lidc_max_sensitiv:</td>
          <td>TBI</td>
        </tr>
        <tr>
          <td>convnet_vgg:</td>
          <td>TBI</td>
        </tr>
        <tr>
          <td>convnett_vgg_lidc:</td>
          <td>TBI</td>
        </tr>
      </tbody>
    </table><br>
    Centroid (predicted):<br>
    <table class="ml-3">
      <tbody>
        <tr>
          <td>Slice:</td>
          <td>TBI</td>
        </tr>
        <tr>
          <td>X:</td>
          <td>{{ candidate.centroid.x }}</td>
        </tr>
        <tr>
          <td>Y:</td>
          <td>{{ candidate.centroid.y }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  props: ['candidate']
}
</script>
