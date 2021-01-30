'''
	This script is expected to run daily with incremental mode 
	which means only new data will be processed and the result will be appended to the sink table.
'''

import pandas as pd

MAX_ROWS = 100
MAX_COLUMNS = 20

pd.set_option("display.max_rows", MAX_ROWS)
pd.set_option("display.max_columns", MAX_COLUMNS)

EMPLOYEES_DATA = "data/employees.csv"
TIMESHEETS_DATA = "data/timesheets.csv"

employees_df = pd.read_csv(EMPLOYEES_DATA, sep=',', header=None, skiprows=1, names=["employee_id", "branch_id", "salary", "join_date", "resign_date"])
timesheets_df = pd.read_csv(TIMESHEETS_DATA, sep=',', header=None, skiprows=1, names=["timesheet_id", "employee_id", "date", "checkin", "checkout"])

# filter out records with missing checkin or checkout
complete_timesheets_df = timesheets_df[timesheets_df[["checkin", "checkout"]].notnull().all(1)]