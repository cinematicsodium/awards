from fiscalyears import FISCAL_YEARS
from processing import process_fiscal_year

for fy in FISCAL_YEARS:
    process_fiscal_year(fy)