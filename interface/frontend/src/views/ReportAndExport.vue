<template>
  <div>
    <h2>Technical parameters</h2>
    <li>kVp: {{ study.kVp }}</li>
    <li>mA: {{ study.mA }}</li>
    <li>DLP: {{ study.DLP }}</li>

    <h2>Clinical information</h2>
    <li>Screening visit: {{ study.screeningVisit }}</li>
    <li>{{ study.clinicalInformation }}</li>


    <h2>Comparison</h2>
    <li>{{ study.comparison }}</li>

    <h2>Findings</h2>
    <h4>Exam parameters</h4>
    <li>Diagnostic quality: {{ study.diagnosticQuality }}</li>
    <li>Comments: {{ study.examParametersComment }}</li>

    <h4>Lung nodules</h4>

    {% for nodule in study.nodules %}
    <li>{{ nodule.diameter }} </li>
    <li>{{ nodule.appearanceFeature }} </li>
    <li>{{ nodule.densityFeature }} </li>
    <li>{{ nodule.imageNo }} </li>
    {% endfor %}

    <li v-for='nodule in study.nodules'>
      <a href='#' @click='selectSeries(series)'>{{ series.series_instance_uid }}</a>
      <span v-if='series == selected'>&larr;</span>
    </li>


    <h4>Lungs</h4>
    <li>COPD: {{ study.COPD }}</li>
    <li>Filiosis: {{ study.filiosis }}</li>
    <li>Lymph nodes: {{ study.lymphNodes }}</li>
    <li>Other findings: {{ study.otherFindings }}</li>

    <h4>Right pleural space</h4>
    <li>Effusion: {{ study.rightPleuralSpace.effusion }}</li>
    <li>Calcification: {{ study.rightPleuralSpace.calcification }}</li>
    <li>Thickening: {{ study.rightPleuralSpace.thickening }}</li>
    <li>Pneumothorax: {{ study.rightPleuralSpace.pneumothorax }}</li>

    <h4>Left pleural space</h4>
    <li>Effusion: {{ study.rightPleuralSpace.effusion }}</li>
    <li>Calcification: {{ study.rightPleuralSpace.calcification }}</li>
    <li>Thickening: {{ study.rightPleuralSpace.thickening }}</li>
    <li>Pneumothorax: {{ study.rightPleuralSpace.pneumothorax }}</li>

    <h4>Heart</h4>
    <li>Heart size: {{ study.heartSize }}</li>
    <li>Coronary calcification: {{ study.coronaryCalcification }}</li>
    <li>Pericardial effusion: {{ study.pericardialEffusion }}</li>

    <h4>Other findings</h4>
    <li>Upper abdomen: {{ study.upper_abdomen }}</li>
    <li>Thorax: {{ study.thorax }}</li>
    <li>Base of neck: {{ study.base_of_neck }}</li>
    <h2>Impression</h2>
    <li>Need comparison: {{ study.need_comparison }}</li>
    <li>Repeat CT: {{ study.repeatCT }}</li>
    <li>See physician: {{ study.see_physician }}</li>
    <li>{{ study.impressionComment }}</li>

  </div>
</template>

<script>
  export default {
    data () {
      return {
        study: {
          kVp: null,
          mA: null,
          DLP: null,
          screeningVisit: 'BL',
          clinicalInformation: '',
          comparison: 'null',
          diagnosticQuality: 'SF',
          examParametersComment: '',
          COPD: 0,
          filiosis: 0,
          lymphNodes: 'null.',
          otherFindings: 'null.',
          rightPleuralSpace: {
            effusion: 0,
            calcification: 0,
            thickening: 0,
            pneumothorax: 0
          },
          leftPleuralSpace: {
            effusion: 0,
            calcification: 0,
            thickening: 0,
            pneumothorax: 0
          },
          heartSize: 0,
          coronaryCalcification: 0,
          pericardialEffusion: 0,
          upperAbdomen: 'null',
          thorax: 'null',
          baseOfNeck: 'null',
          needComparison: 'No',
          repeatCT: 'T1',
          seePhysician: 'NO',
          impressionComment: ''
        },
        nodule: []
      }
    }
  }
</script>
