<template>
  <div class="rsna-standard-template-container">
  <div class="float-right">
    <button class="btn btn-lg btn-warning" @click='exportRSNA()'>Export</button>
  </div>
  <h1>
    RSNA Standard Template
  </h1>
  <hr>

  <section id="technical-parameters">
    <h2>Technical parameters</h2>
    <article>
      <olp label='kVp' :value='technical.kVp.value'></olp>
      <olp label='mA' :value='technical.mA.value'></olp>
      <olp label='DLP' :value='technical.DLP.value + " " + technical.DLP.unit'></olp>
    </article>
  </section>

  <section id="clinical-information">
    <h2>Clinical information</h2>
    <article>
      <olp label='Screening visit' :value='clinical.visit'></olp>
      <p>
        {{ clinical.reason }}
      </p>
    </article>
  </section>

  <section id="findings">
    <h2>Findings</h2>
    <!-- {{findings}} -->

    <article>
      <!-- {{ findings.exam }} -->
      <h3>Exam parameters</h3>
      <olp label='Diagnostic quality'
        constant-key="DIAGNOSTIC_QUALITY_STRINGS"
        :value='findings.exam.diagnosticQuality'></olp>
      <olp label='Comments' :value='findings.exam.comments'></olp>
    </article>

    <article>
      <!-- {{findings.lungNodules}} -->
      <h3>Lung nodules</h3>
      <p v-if="findings.lungNodules.length === 0">
        None.
      </p>

      <div class="nodule-list" v-else>

        <div class="card" v-for="(nodule, index) in findings.lungNodules" :nodule="nodule" :index="index" :key="index">
          <div class="card-header">
            <h3>Nodule {{ index + 1}}</h3>
          </div>
          <div class="nodule-info-container">
            <!-- {{ nodule }} -->
            <div class="nodule-info">
              <olp label='Position'
                constant-key="LUNG_ORIENTATION_STRINGS"
               :value='nodule.lung_orientation'></olp>
              <olp label='Size'
                :value='nodule.size + "mm"'></olp>
              <olp label='Density'
              constant-key="DENSITY_STRINGS"
              :value='nodule.density_feature'></olp>
              <olp label='Condition'
                constant-key="SIZE_CHANGE_STRINGS"
                 :value='nodule.condition'></olp>
            </div>
            <div class="nodule-image m-2">
              <img src="../../assets/images/sample-nodule.png" alt="Nodule Image">
            </div>
          </div>
        </div>

      </div>

    </article>

    <article>
      <!-- {{findings.lungs}} -->
      <h3>Lungs</h3>
      <olp label='COPD'
        constant-key="SEVERITY_STRINGS"
        :value='findings.lungs.copd'></olp>
      <olp label='Fibrosis'
        constant-key="SEVERITY_STRINGS"
        :value='findings.lungs.fibrosis'></olp>
      <olp label='Lymph nodes' :value='findings.lungs.lymphNodes'></olp>
      <olp label='Other findings' :value='findings.lungs.otherFindings'></olp>
    </article>

    <article>
      <!-- {{findings.rightPleuralSpace}} -->
      <h3>Right pleural space</h3>
      <olp label='Effusion'
        constant-key="SIZE_STRINGS"
        :value='findings.rightPleuralSpace.effusion'></olp>

      <olp label='Calcification'
        constant-key="SPREAD_STRINGS"
        :value='findings.rightPleuralSpace.calcification'></olp>

      <olp label='Thickening'
        constant-key="SPREAD_STRINGS"
        :value='findings.rightPleuralSpace.thickening'></olp>

      <olp label='Pneumothorax'
        constant-key="SIZE_STRINGS"
        :value='findings.rightPleuralSpace.pneumothorax'></olp>
    </article>

    <article>
      <!-- {{findings.leftPleuralSpace}} -->
      <h3>Left pleural space</h3>

      <olp label='Effusion'
        constant-key="SIZE_STRINGS"
        :value='findings.leftPleuralSpace.effusion'></olp>

      <olp label='Calcification'
        constant-key="SPREAD_STRINGS"
        :value='findings.leftPleuralSpace.calcification'></olp>

      <olp label='Thickening'
        constant-key="SPREAD_STRINGS"
        :value='findings.leftPleuralSpace.thickening'></olp>

      <olp label='Pneumothorax'
        constant-key="SIZE_STRINGS"
        :value='findings.leftPleuralSpace.pneumothorax'></olp>
    </article>

    <article>
      <!-- {{findings.heart}} -->
      <h3>Heart</h3>
      <olp label='Heart size'
        constant-key="HEART_ENLARGEMENT_STRINGS"
        :value='findings.heart.sizeEnlargement'></olp>

      <olp label='Coronary calcification'
        constant-key="SEVERITY_STRINGS"
        :value='findings.heart.coronaryCalcification'></olp>

      <olp label='Pericardial effusion'
        constant-key="SEVERITY_STRINGS"
        :value='findings.heart.pericardialEffusion'></olp>
    </article>

    <article>
      <!-- {{findings.other}} -->
      <h3>Other findings</h3>
      <olp label='Upper abdomen'
        :value='findings.other.upperAbdomen'></olp>

      <olp label='Thorax'
        :value='findings.other.thorax'></olp>

      <olp label='Base of neck'
        :value='findings.other.baseOfNeck'></olp>
    </article>

  </section>

  <section id="impression">
    <h2>Impression</h2>
    <!-- {{ impression }} -->
    <article>
      <olp label='Need comparison' :value='impression.needComparison'></olp>

      <olp label='Repeat CT'
                constant-key='REPEAT_CT_STRING'
                :value='impression.repeatCT'></olp>

      <olp label='See physician' :value='impression.seePhysician'></olp>

      <olp label='Comments' :value='impression.comments'></olp>
    </article>
  </section>
</div>
</template>

<script>
import OneLineParagraph from './OneLineParagraph'

import Nodule from '../annotate-and-segment/Nodule'
import html2canvas from 'html2canvas'
import JSPDF from 'jspdf'

export default {
  components: {
    'olp': OneLineParagraph,
    Nodule
  },
  data () {
    return {
      ...this.rsna
    }
  },
  props: [ 'rsna' ],
  methods: {
    exportRSNA () {
      // specified the column with all the 3 components in the view
      const pdfSection = this.$refs.pdfSection
      html2canvas(pdfSection).then(canvas => {
        const imgData = canvas.toDataURL('image/png')
        /* https://github.com/MrRio/jsPDF/issues/434 @wangzhixuan answer */
        const imgWidth = 210
        const pageHeight = 295
        const imgHeight = canvas.height * imgWidth / canvas.width
        let heightLeft = imgHeight
        const doc = new JSPDF('p', 'mm')
        let position = 0
        doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
        heightLeft -= pageHeight
        while (heightLeft >= 0) {
          position = heightLeft - imgHeight
          doc.addPage()
          doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
          heightLeft -= pageHeight
        }
        doc.save('rsna-standard-template.pdf')
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.rsna-standard-template-container {
  .custom-control {
    margin: 0;
  }

  section {
    padding-left: 2em;
    margin-bottom: 3em;
  }

  article {
    margin-left: 1em;
    font-size: 1.35em;
    margin-bottom: 2em;
    h3 {
      margin-bottom: 1em;
    }
    p {
      margin-left: 1em;
    }

    .nodule-list {
      padding: 0 1em;

      .nodule-info-container {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
      }

      .nodule-image img {
        height: 9em;
        transition: 0.5s;
        &:hover {
          height: 18em;
        }
      }

    }
  }

  .flex-space-around {
    display: flex;
    justify-content: space-around;
  }
}
</style>
