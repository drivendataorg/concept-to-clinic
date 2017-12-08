<template>
  <div class="card-block">
    Centroid (predicted):<br>
    <table class="ml-3">
      <tbody>
        <tr>
          <td>X:</td>
          <td><strong>{{ candidate.centroid.x }}</strong></td>
        </tr>
        <tr>
          <td>Y:</td>
          <td><strong>{{ candidate.centroid.y }}</strong></td>
        </tr>
        <tr>
          <td class="pr-3">Slice index: </td>
          <td><strong>{{ candidate.centroid.z }}</strong></td>
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
