<template lang="html">

	<div class="technical-card">
		<label>{{detail.name}}</label>
		<div class="technical-data">
			<h2>{{detail.value}}</h2>
			<h3>{{detail.unit}}</h3>
		</div>
	</div>
</template>

<script>
export default {
  props: ['detail']
}
</script>

<style lang="scss">
.technical-card {
    border-radius: 5px;

    position: relative;

    display: flex;

    justify-content: center;
    align-items: center;

    width: 270px;
    height: 135px;

    color: white;
		text-shadow: 0 2px 5px rgba(0, 0, 0, .5);
		box-shadow: 2px 2px 5px rgba(0, 0, 0, .5);

		transition: 0.5s ease;

		&:hover {
			transform: scale(1.18);
			z-index: 9999;
		}

    .technical-data {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    label {
        position: absolute;
        left: 0;
        bottom: 0;
        margin: 0;

				font-size: 1.5em;
				padding: 0.36em;

				background: #4C8DDA;

				border-top: 2px white solid;
				border-right: 2px white solid;

				border-bottom-left-radius: 5px;
				border-top-right-radius: 5px;

				box-shadow: 5px 0 10px rgba(0, 0, 0, .5);

    }

    h2 {
				margin: 0;
        font-size: 3em;
        text-align: center;
    }

    h3 {
        font-size: 1.44em;
    }
}
</style>
