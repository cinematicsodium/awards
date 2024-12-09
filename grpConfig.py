from dataclasses import dataclass
from modules import EmpInfo


MAX_14: tuple[EmpInfo] = (
    EmpInfo('employee name_2','immediate supervisor','organization_7','pay plan  gradestep_2','award amount','time off hours'),
    EmpInfo('employee name_3','immediate supervisor_2','organization_8','pay plan  gradestep_3','award amount_2','time off hours_2'),
    EmpInfo('employee name_4','immediate supervisor_3','organization_9','pay plan  gradestep_4','award amount_3','time off hours_3'),
    EmpInfo('employee name_5','immediate supervisor_4','organization_10','pay plan  gradestep_5','award amount_4','time off hours_4'),
    EmpInfo('employee name_6','immediate supervisor_5','organization_11','pay plan  gradestep_6','award amount_5','time off hours_5'),
    EmpInfo('employee name_7','immediate supervisor_6','organization_12','pay plan  gradestep_7','award amount_6','time off hours_6'),
    EmpInfo('employee name_8','immediate supervisor_7','organization_13','pay plan  gradestep_8','award amount_7','time off hours_7'),
    EmpInfo('employee name_9','immediate supervisor_8','organization_14','pay plan  gradestep_9','award amount_8','time off hours_8'),
    EmpInfo('employee name_10','immediate supervisor_9','organization_15','pay plan  gradestep_10','award amount_9','time off hours_9'),
    EmpInfo('employee name_11','immediate supervisor_10','organization_16','pay plan  gradestep_11','award amount_10','time off hours_10'),
    EmpInfo('employee name_12','immediate supervisor_11','organization_17','pay plan  gradestep_12','award amount_11','time off hours_11'),
    EmpInfo('employee name_13','immediate supervisor_12','organization_18','pay plan  gradestep_13','award amount_12','time off hours_12'),
    EmpInfo('employee name_14','immediate supervisor_13','organization_19','pay plan  gradestep_14','award amount_13','time off hours_13'),
    EmpInfo('employee name_15','immediate supervisor_14','organization_20','pay plan  gradestep_15','award amount_14','time off hours_14'),
)


MAX_21: tuple[EmpInfo] = (
    EmpInfo('employee name_1', 'immediate supervisor', 'organization_1', 'pay plan  gradestep_1', 'award amount', 'time off hours'),
    EmpInfo('employee name_2', 'immediate supervisor_2', 'organization_2', 'pay plan  gradestep_2', 'award amount_2', 'time off hours_2'),
    EmpInfo('employee name_3', 'immediate supervisor_3', 'organization_3', 'pay plan  gradestep_3', 'award amount_3', 'time off hours_3'),
    EmpInfo('employee name_4', 'immediate supervisor_4', 'organization_4', 'pay plan  gradestep_4', 'award amount_4', 'time off hours_4'),
    EmpInfo('employee name_5', 'immediate supervisor_5', 'organization_5', 'pay plan  gradestep_5', 'award amount_5', 'time off hours_5'),
    EmpInfo('employee name_6', 'immediate supervisor_6', 'organization_6', 'pay plan  gradestep_6', 'award amount_6', 'time off hours_6'),
    EmpInfo('employee name_7', 'immediate supervisor_7', 'organization_7', 'pay plan  gradestep_7', 'award amount_7', 'time off hours_7'),
    EmpInfo('employee name_8', 'immediate supervisor_8', 'organization_8', 'pay plan  gradestep_8', 'award amount_8', 'time off hours_8'),
    EmpInfo('employee name_9', 'immediate supervisor_9', 'organization_9', 'pay plan  gradestep_9', 'award amount_9', 'time off hours_9'),
    EmpInfo('employee name_10', 'immediate supervisor_10', 'organization_10', 'pay plan  gradestep_10', 'award amount_10', 'time off hours_10'),
    EmpInfo('employee name_11', 'immediate supervisor_11', 'organization_11', 'pay plan  gradestep_11', 'award amount_11', 'time off hours_11'),
    EmpInfo('employee name_12', 'immediate supervisor_12', 'organization_12', 'pay plan  gradestep_12', 'award amount_12', 'time off hours_12'),
    EmpInfo('employee name_13', 'immediate supervisor_13', 'organization_13', 'pay plan  gradestep_13', 'award amount_13', 'time off hours_13'),
    EmpInfo('employee name_14', 'immediate supervisor_14', 'organization_14', 'pay plan  gradestep_14', 'award amount_14', 'time off hours_14'),
    EmpInfo('employee name_15', 'immediate supervisor_15', 'organization_15', 'pay plan  gradestep_15', 'award amount_15', 'time off hours_15'),
    EmpInfo('employee name_16', 'immediate supervisor_16', 'organization_16', 'pay plan  gradestep_16', 'award amount_16', 'time off hours_16'),
    EmpInfo('employee name_17', 'immediate supervisor_17', 'organization_17', 'pay plan  gradestep_17', 'award amount_17', 'time off hours_17'),
    EmpInfo('employee name_18', 'immediate supervisor_18', 'organization_18', 'pay plan  gradestep_18', 'award amount_18', 'time off hours_18'),
    EmpInfo('employee name_19', 'immediate supervisor_19', 'organization_19', 'pay plan  gradestep_19', 'award amount_19', 'time off hours_19'),
    EmpInfo('employee name_20', 'immediate supervisor_20', 'organization_20', 'pay plan  gradestep_20', 'award amount_20', 'time off hours_20'),
    EmpInfo('employee name_21', 'immediate supervisor_21', 'organization_21', 'pay plan  gradestep_21', 'award amount_21', 'time off hours_21'),
)

GrpConfig: dict[int, tuple[EmpInfo]] = {
    4: MAX_14,
    5: MAX_21
}