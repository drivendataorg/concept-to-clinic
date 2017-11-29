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
          <td><b>{{ candidate.centroid.x }}</b></td>
        </tr>
        <tr>
          <td>Y:</td>
          <td><b>{{ candidate.centroid.y }}</b></td>
        </tr>
        <tr>
          <td class="pr-3">Slice index: </td>
          <td><b>{{ candidate.centroid.z }}</b></td>
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
