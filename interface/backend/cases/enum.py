from enum import IntEnum, unique, Enum


def django_enum(cls):
    # decorator needed to enable enums in django templates
    cls.do_not_call_in_templates = True
    return cls


def format_enum(enum: Enum):
    return [(choice.value, choice.name.replace("_", " ")) for choice in enum]


DIAGNOSTIC_QUALITY_CHOICES = (
    ("SF", "Satisfactory"),
    ("LI", "Limited, but interpretable"),
    ("ND", "Non - diagnostic")
)
PERIODS = (
    ("T1", "12 months from screening exam"),
    ("T2", "3 months from screening exam"),
    ("T3", "6 months from screening exam"),
    ("T4", "3 to 6 months from screening exam"),
    ("T5", "24 months from screening exam")
)
PHYSICIAN = (
    ("NO", "No."),
    ("YC", "Yes, Suspect cancer."),
    ("YM", "Yes, non - malignant finding.")
)
SCREENING_VISIT_CHOICES = (
    ("BL", "Baseline"),
    ("Y1", "Year 1"),
    ("Y2", "Year 2")
)


@unique  # ensures all variables are unique
@django_enum
class TypesOne(IntEnum):
    NONE = 0
    SMALL = 1
    MODERATE = 2
    LARGE = 3


@unique  # ensures all variables are unique
@django_enum
class TypesTwo(IntEnum):
    NONE = 0
    MILD = 1
    MODERATE = 2
    EXTENSIVE = 3


@unique  # ensures all variables are unique
@django_enum
class ShapeChoices(IntEnum):
    NONE = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3


@unique  # ensures all variables are unique
@django_enum
class HeartShapeChoices(IntEnum):
    NORMAL = 0
    MILDLY_ENLARGED = 1
    MODERATELY_ENLARGED = 2
    SEVERELY_ENLARGED = 3


@unique  # ensures all variables are unique
@django_enum
class LungOrientation(IntEnum):
    NONE = 0
    LEFT = 1
    RIGHT = 2


@unique  # ensures all variables are unique
@django_enum
class AppearanceFeature(IntEnum):
    NONE = 0
    UNCHANGED = 1
    INCREASED = 2
    DECREASED = 3
    NEW = 4


@unique  # ensures all variables are unique
@django_enum
class DensityFeature(IntEnum):
    NONE = 0
    SOLID = 1
    SEMI_SOLID = 2
    GROUND_GLASS = 3
