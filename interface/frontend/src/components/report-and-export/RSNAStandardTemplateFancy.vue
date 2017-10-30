<template>
<div class="rsna-fancy-container">
  <section id="technical-parameters">
    <h2>Technical parameters</h2>

    <div class="flex-space-around">
      <technical-card v-for="(item, index) in technical"
        :key="item.name"
        :detail="item"
        :style="{background: technicalBackground[index]}">
      </technical-card>
    </div>

  </section>

  <section id="clinical-information">
    <h2>Clinical information</h2>
    <div class="flex-space-around">
      <technical-card :detail="clinical"
        :style="{
          width: '50%',
          height: '13em',
          background: technicalBackground[0]
        }"></technical-card>
    </div>
  </section>
</div>
</template>

<script>
import TechnicalCard from './TechnicalCard'

export default {
  components: {
    TechnicalCard
  },
  data () {
    return {
      technicalBackground: ['#60D9F1', '#5770F9', '#453DF4']
    }
  },
  computed: {
    clinical: function () {
      return {
        name: 'Screening Visit',
        value: this.rsna.clinical.visit,
        unit: this.rsna.clinical.reason
      }
    },
    technical: function () {
      return Object.keys(this.rsna.technical)
      .map(key => {
        return {
          name: key,
          ...this.rsna.technical[key]
        }
      })
    }
  },
  props: [ 'rsna' ]
}
</script>

<style lang="scss" scoped>
.rsna-fancy-container {

  h2 {
    padding-top: 0.5em;
    margin-bottom: 0.5em;
  }

  h3 {
    padding-left: 2em;
  }

  section {
    padding-left: 2em;
    margin-bottom: 3em;
  }

  .flex-space-around {
    display: flex;
    justify-content: space-around;
  }
}
</style>
