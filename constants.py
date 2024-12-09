from dataclasses import dataclass
import grpConfig

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# AWARD CONSTANTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
PAY_PLANS = ('ED', 'EN', 'ES', 'NQ', 'SL')


@dataclass(frozen=True)
class RatingScale:
    VALUES: tuple[str, ...] = ('moderate', 'high', 'exceptional')
    EXTENTS: tuple[str, ...] = ('limited', 'extended', 'general')
RATING_SCALE = RatingScale()
VALUE_IDX_MAP = {value: idx for idx, value in enumerate(RATING_SCALE.VALUES)}
EXTENT_IDX_MAP = {extent: idx for idx, extent in enumerate(RATING_SCALE.EXTENTS)}


@dataclass(frozen=True)
class MaxValuesConfig:
    MONETARY: tuple = (
        (500, 1000, 3000),      # moderate
        (1000, 3000, 6000),     # high
        (3000, 6000, 10000),    # exceptional
    )
    HOURS: tuple = (
        (9, 18, 27),   # moderate
        (18, 27, 36),  # high
        (27, 36, 40),  # exceptional
    )
MAX_VALUES = MaxValuesConfig()
MONETARY_LIMITS = MAX_VALUES.MONETARY
HOURS_LIMITS = MAX_VALUES.HOURS


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PDF / FIELD CONSTANTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@dataclass(frozen=True)
class PageCountConfig:
    ind: int = 2
    grp_max_7: int = 3
    grp_max_14: int = 4
    grp_max_21: int = 5
PAGE_COUNTS = PageCountConfig()


FUNDING_ORG_FIELDS: tuple[str, ...] = ('org', 'org_2', 'org_3', 'org_4', 'org_6')


@dataclass(frozen=True)
class ValueFields:
    monetary: str
    hours: str
    def combined(self) -> tuple[str, str]:
        return self.monetary, self.hours


SAS_FIELDS = ValueFields(
    monetary='undefined',
    hours='hours_2',
)


OTS_FIELDS = ValueFields(
    monetary='on the spot award',
    hours='hours',
)


@dataclass(frozen=True)
class CommonFields:
    nominator_name: str = 'please print'
    date_received: str = 'date received'
    effective_date: str = 'effective date'
    noac_code: str = 'noac'
    justification: str = 'extent of application'
    values: tuple[str, ...] = RatingScale().VALUES
    extents: tuple[str, ...] = RatingScale().EXTENTS
    funding_orgs: tuple[str, ...] = FUNDING_ORG_FIELDS
    sas_fields: ValueFields = SAS_FIELDS
    ots_fields: ValueFields = OTS_FIELDS
COMMON_FIELDS = CommonFields()


@dataclass(frozen=True)
class IndFields(CommonFields):
    employee_name: str = 'employee name'
    employee_org: str = 'organization'
    employee_pay_plan: str = 'pay plan gradestep 1'
    supervisor: str = 'please print_2'
IND_FIELDS = IndFields()


@dataclass(frozen=True)
class GrpMax14Fields(CommonFields):
    employees = grpConfig.MAX_14
GRP_MAX_14_FIELDS = GrpMax14Fields()


@dataclass(frozen=True)
class GrpMax21Fields(CommonFields):
    employees = grpConfig.MAX_21
GRP_MAX_21_FIELDS = GrpMax21Fields()