export default {
  LUNG_ORIENTATION: {
    NONE: 0,
    LEFT: 1,
    RIGHT: 2
  },
  DIAGNOSTIC_QUALITY: {
    NONE: 'Non-diagnostic',
    LIMITED: 'Limited, but interpretable',
    SATISFACTORY: 'Satisfactory'
  },
  SOLIDITY: {
    SOLID: 'Solid',
    SEMI_SOLID: 'Semi-solid',
    GROUND_GLASS: 'Ground glass'
  },
  CONDITION: {
    UNCHANGED: 'Unchanged',
    INCREASED: 'Increased',
    DECREASED: 'Decreased',
    NEW: 'New'
  },
  SEVERITY: {
    NONE: 0,
    MILD: 1,
    MODERATE: 2,
    SEVERE: 3
  },
  SPREAD: {
    NONE: 0,
    MILD: 1,
    MODERATE: 2,
    EXTENSIVE: 3
  },
  SIZE: {
    NONE: 0,
    SMALL: 1,
    MODERATE: 2,
    LARGE: 3
  },
  PHYSICIAN_VISIT: {
    NO: 'No',
    YES_CANCER: 'YES. Suspect cancer',
    YES_NON_MALIGNANT: 'YES, non-malignant finding'
  },
  REPEAT_CT: {
    THREE_MONTH: '3 months from screening exam',
    SIX_MONTH: '6 months from screening exam',
    THREE_TO_SIX_MONTH: '3 to 6 months from screening exam',
    TWELVE_MONTH: '12 months from screening exam',
    TWENTY_FOUR_MONTH: '24 months from screening exam'
  }
}
