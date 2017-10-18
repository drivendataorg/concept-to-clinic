<template>
<div id="annotate" class="container">
  <div class="card-header row-space-between">
    <h1>Nodule 1 (predicted)</h1>
    <a @click="update(nodule)">
        <button type="button" class="btn btn-sm btn-success">Accept</button>
      </a>
  </div>

  <div class="concern-slider-container">
    <div class="concern-labels row-space-between">
      <span>Not concerning</span>
      <span>Concerning</span>
    </div>
    <div class="concern-slider">
      <input id="test" type="range" />
    </div>
    <div class="concern-value row-space-between">
      <span class="predicted">
					<span class="label">Predicted</span>
      <span class="value">98%</span>
      </span>
      <span class="labeled">
					<span class="label">Labeled</span>
      <span class="value">100%</span>
      </span>
    </div>

    <div class="lung-select-container">
      <select>
					<option>Left lung</option>
					<option>Right lung</option>
				</select>
    </div>

    <div class="solidity-radio-container">
      <form>
        <input type="radio" name="solidity" value="solid" checked> Solid
				<br>
        <input type="radio" name="solidity" value="semi-solid"> Semi-solid
				<br>
        <input type="radio" name="solidity" value="ground-glass"> Ground glass
      </form>
    </div>

    <div class="severity-radio-container">
			<form>
				<input type="radio" name="severity" value="unchaged" checked> Unchanged
				<br>
				<input type="radio" name="severity" value="increased"> Increased
				<br>
				<input type="radio" name="severity" value="decreased"> Decreased
				<br>
				<input type="radio" name="severity" value="new"> New
			</form>
    </div>

    <div class="note-container">
      <textarea name="name" rows="3" style="width:100%;" placeholder="Add notes">
			</textarea>
    </div>

  </div>
</div>
</template>

<script>
export default {
  props: ['nodule', 'index']
}
</script>

<style scoped>
.container {
  width: 45vw;
  display: flex;
  flex-direction: column;
}

.row-space-between {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.card-header {
  align-items: center;
  height: 90px;
  padding: 1em;
}

.card-header h1 {
  margin: 0;
  font-size: 1em;
  font-weight: bold;
}

.concern-labels {
  margin: 1em;
}

.concern-slider {
  display: flex;
  justify-content: center;
}

.concern-slider input {
  width: 100%;
  margin: 1em;
}
</style>
