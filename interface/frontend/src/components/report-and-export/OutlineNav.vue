<template lang="html">
	<div class="outline-nav">
		<h1 class="bg-inverse">Outline</h1>
		<ul>
			<li v-for='{name, id} in outlines'
					@click='jumpToOutline(id)'
					:class="{
							'active' : id === value
						}">
					{{ name }}
			</li>
		</ul>
	</div>
</template>

<script>
export default {
  props: ['outlines', 'value'],
  methods: {
    jumpToOutline (id) {
      this.$emit('input', id)
    }
  }
}
</script>

<style lang="scss">
.outline-nav {
    h1 {
        color: white;

        font-size: 2.5em;

        line-height: 2em;
        padding-left: 1em;
        font-weight: normal;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    ul {
        list-style: none;
        margin-top: 0;
        padding: 0;

        li {
						height: 4em;
            padding-left: 4em;
            background-color: #383B42;
            border-bottom: 1px solid #2E3036;
            transition: 0.6s;

						font-size: 1.20em;

						text-decoration: none;

						line-height: 1em;

						display: flex;
						align-items: center;

						position: relative;
						letter-spacing: 1px;
						transition: all 0.6s;
						color: #b3b3b3;

            &:hover {
                cursor: pointer;
                background-color: #454952;
								color: #fff;
            }

            &.active {
                box-shadow: 5px 0 5px rgba(0, 0, 0, 1);
                background-color: white;
                color: black;
            }
        }
    }
}
</style>
