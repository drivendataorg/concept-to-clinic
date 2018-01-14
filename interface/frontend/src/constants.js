export default {
  LUNG_ORIENTATION: {
    NONE: 0,
    LEFT: 1,
    RIGHT: 2
  },
  LUNG_ORIENTATION_STRINGS: ['None', 'Left', 'Right'],
  DIAGNOSTIC_QUALITY: {
    NONE: 0,
    LIMITED: 1,
    SATISFACTORY: 2
  },
  DIAGNOSTIC_QUALITY_STRINGS: [
    'Non-diagnostic',
    'Limited, but interpretable',
    'Satisfactory'
  ],
  DENSITY: {
    SOLID: 0,
    SEMI_SOLID: 1,
    GROUND_GLASS: 2
  },
  DENSITY_STRINGS: [
    'Solid',
    'Semi-solid',
    'Ground glass'
  ],
  SIZE_CHANGE: {
    UNCHANGED: 0,
    INCREASED: 1,
    DECREASED: 2,
    NEW: 3
  },
  SIZE_CHANGE_STRINGS: [
    'Unchanged',
    'Increased',
    'Decreased',
    'New'
  ],
  SEVERITY: {
    NONE: 0,
    MILD: 1,
    MODERATE: 2,
    SEVERE: 3
  },
  SEVERITY_STRINGS: [
    'None',
    'Mild',
    'Moderate',
    'Severe'
  ],
  HEART_ENLARGEMENT_STRINGS: [
    'Normal',
    'Mildly enlarged',
    'Moderately enlarged',
    'Severely enlarged'
  ],
  SPREAD: {
    NONE: 0,
    MILD: 1,
    MODERATE: 2,
    EXTENSIVE: 3
  },
  SPREAD_STRINGS: [
    'None',
    'Mild',
    'Moderate',
    'Extensive'
  ],
  SIZE: {
    NONE: 0,
    SMALL: 1,
    MODERATE: 2,
    LARGE: 3
  },

  SIZE_STRINGS: [
    'None',
    'Small',
    'Moderate',
    'Large'
  ],
  PHYSICIAN_VISIT: {
    NO: 0,
    YES_CANCER: 1,
    YES_NON_MALIGNANT: 2
  },
  PHYSICIAN_VISIT_STRINGS: [
    'No',
    'YES. Suspect cancer',
    'YES, non-malignant finding'
  ],
  REPEAT_CT: {
    THREE_MONTH: 0,
    SIX_MONTH: 1,
    THREE_TO_SIX_MONTH: 2,
    TWELVE_MONTH: 3,
    TWENTY_FOUR_MONTH: 4
  },
  REPEAT_CT_STRING: [
    '3 months from screening exam',
    '6 months from screening exam',
    '3 to 6 months from screening exam',
    '12 months from screening exam',
    '24 months from screening exam'
  ],
  CANDIDATE_REVIEW_RESULT: {
    NONE: 0,
    MARKED: 1,
    DISMISSED: 2
  }
}
