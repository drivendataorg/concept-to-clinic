<template>
<div class="offset-top container">
  <div class="row">
    <div class='col-md-3'>
      <outline-nav :outlines="outlines" v-model="activeOutlineId"></outline-nav>
    </div>

    <div class='col-md-9' ref='pdfSection'>
      <rsna-standard-template
        v-show="activeOutlineId === '#RSNA'"
        :rsna="study">
      </rsna-standard-template>

      <acr-lung-rad-findings
        v-show="activeOutlineId === '#ACR'">
      </acr-lung-rad-findings>

      <export-3d-imagery
        v-show="activeOutlineId === '#Export3D'">
      </export-3d-imagery>

    </div>

  </div>

</div>
</template>

<script>
import OutlineNav from '../components/report-and-export/OutlineNav'

import RSNAStandardTemplate from '../components/report-and-export/RSNAStandardTemplate'
import ACRLungRADFindings from '../components/report-and-export/ACRLungRADFindings'
import Export3DImagery from '../components/report-and-export/Export3DImagery'

export default {
  components: {
    OutlineNav,
    'rsna-standard-template': RSNAStandardTemplate,
    'acr-lung-rad-findings': ACRLungRADFindings,
    'export-3d-imagery': Export3DImagery
  },
  data () {
    return {
      activeOutlineId: '#RSNA',
      outlines: [
        // {
        //   name: 'Overview',
        //   id: '#Overview'
        // },
        {
          name: 'RSNA Standard Template',
          id: '#RSNA'
        },
        {
          name: 'ACR Lung-RAD™ Findings',
          id: '#ACR'
        },
        {
          name: 'Export 3D Imagery',
          id: '#Export3D'
        }
      ],
      study: {
        technical: {
          kVp: {
            value: 120
          },
          mA: {
            value: 93
          },
          DLP: {
            value: 18,
            unit: 'µSv/mGy'
          }
        },
        clinical: {
          visit: 'Year 1',
          reason: 'Lung cancer screening'
        },
        comparison: 'None.',
        findings: {
          exam: {
            diagnosticQuality: this.$constants.DIAGNOSTIC_QUALITY.SATISFACTORY,
            comments: 'None.'
          },
          lungNodules: [{
            size: 3,
            density: this.$constants.DENSITY.SOLID,
            lung_orientation: this.$constants.LUNG_ORIENTATION.LEFT,
            condition: this.$constants.SIZE_CHANGE.INCREASED,
            image: null
          }],
          lungs: {
            copd: this.$constants.SEVERITY.SEVERE,
            fibrosis: this.$constants.SEVERITY.MILD,
            lymphNodes: 'None.',
            otherFindings: 'None.'
          },
          rightPleuralSpace: {
            effusion: this.$constants.SIZE.MODERATE,
            calcification: this.$constants.SPREAD.EXTENSIVE,
            thickening: this.$constants.SPREAD.NONE,
            pneumothorax: this.$constants.SIZE.LARGE
          },
          leftPleuralSpace: {
            effusion: this.$constants.SIZE.MODERATE,
            calcification: this.$constants.SPREAD.EXTENSIVE,
            thickening: this.$constants.SPREAD.NONE,
            pneumothorax: this.$constants.SIZE.LARGE
          },
          heart: {
            sizeEnlargement: this.$constants.SIZE.LARGE,
            coronaryCalcification: this.$constants.SEVERITY.MODERATE,
            pericardialEffusion: this.$constants.SEVERITY.SEVERE
          },
          other: {
            upperAbdomen: 'None.',
            thorax: 'None.',
            baseOfNeck: 'None.'
          }
        },
        impression: {
          needComparison: 'Yes',
          repeatCT: this.$constants.REPEAT_CT.SIX_MONTH,
          seePhysician: this.$constants.PHYSICIAN_VISIT.YES_CANCER,
          comments: 'None.'
        }
      }
    }
  }
}
</script>
