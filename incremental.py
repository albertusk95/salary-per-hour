'''
	This script is expected to run daily with incremental mode 
	which means only new data will be processed and the result will be appended to the sink table.
'''

import argparse
import pandas as pd
import sqlalchemy

MAX_ROWS = 100
MAX_COLUMNS = 20

pd.set_option("display.max_rows", MAX_ROWS)
pd.set_option("display.max_columns", MAX_COLUMNS)

def extract_data(PATH: str, cols: [str]):
	return pd.read_csv(PATH, sep=',', header=None, skiprows=1, names=cols)

def store_data(user: str, db_pass: str, host: str, port: str, db_name: str, df: pd.DataFrame):
	db_conn = sqlalchemy.create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(user, db_pass, host, port, db_name))
	df.to_sql(con=db_conn, name='salary_per_hour_incremental', if_exists='append')


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--user", help="Database user")
	parser.add_argument("-p", "--dbpass", help="Database password")
	parser.add_argument("-ho", "--host", help="Database host", default="localhost")
	parser.add_argument("-po", "--port", help="Database port", default="3306")
	parser.add_argument("-db", "--dbname", help="Database name", default="salary_per_hour_db")

	args = parser.parse_args()
	user = args.user
	db_pass = args.dbpass
	host = args.host
	port = args.port
	db_name = args.dbname

	EMPLOYEES_DATA = "data/employees.csv"
	TIMESHEETS_DATA = "data/timesheets.csv"

	'''
		Extract
	'''
	employees_df = extract_data(EMPLOYEES_DATA, cols=["employee_id", "branch_id", "salary", "join_date", "resign_date"])
	timesheets_df = extract_data(TIMESHEETS_DATA, cols=["timesheet_id", "employee_id", "date", "checkin", "checkout"])

	'''
		Transform
	'''
	# filter out records with missing checkin or checkout
	complete_timesheets_df = timesheets_df[timesheets_df[["checkin", "checkout"]].notnull().all(1)]

	'''
		Load
	'''
	store_data(user=user, db_pass=db_pass, host=host, port=port, db_name=db_name, df=complete_timesheets_df)
