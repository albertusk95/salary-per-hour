'''
	This script is expected to run daily with incremental mode 
	which means only new data will be processed and the result will be appended to the sink table.
'''

from datetime import datetime

import argparse
import pandas as pd
import sqlalchemy

MAX_ROWS = 300
MAX_COLUMNS = 20

pd.set_option("display.max_rows", MAX_ROWS)
pd.set_option("display.max_columns", MAX_COLUMNS)

def extract_employees_data(PATH: str, cols: [str]):
	return pd.read_csv(PATH, sep=',', header=None, skiprows=1, names=cols)

def extract_timesheets_data(PATH: str, cols: [str]):
	current_date = datetime.date(datetime.now())
	
	iter_csv = pd.read_csv(PATH, sep=',', header=None, skiprows=1, names=cols, iterator=True, chunksize=100)
	return pd.concat([chunk[chunk['date'] == current_date.strftime('%Y-%m-%d')] for chunk in iter_csv])

def store_data(user: str, db_pass: str, host: str, port: str, db_name: str, df: pd.DataFrame):
	db_conn = sqlalchemy.create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(user, db_pass, host, port, db_name))
	df.to_sql(con=db_conn, name='salary_per_hour_incremental', if_exists='append')

def filter_out_missing_time(df: pd.DataFrame):
	return df[df[["checkin", "checkout"]].notnull().all(1)]

def add_date_to_checkin_and_checkout(df: pd.DataFrame):
	df[['checkin_h', 'checkin_m', 'checkin_s']] = df["checkin"].str.split(':', 3, expand=True)
	df[['checkout_h', 'checkout_m', 'checkout_s']] = df["checkout"].str.split(':', 3, expand=True)

	df.checkin_h = pd.to_numeric(df["checkin_h"], errors='coerce')
	df.checkin_m = pd.to_numeric(df["checkin_m"], errors='coerce')
	df.checkin_s = pd.to_numeric(df["checkin_s"], errors='coerce')

	df.checkout_h = pd.to_numeric(df["checkout_h"], errors='coerce')
	df.checkout_m = pd.to_numeric(df["checkout_m"], errors='coerce')
	df.checkout_s = pd.to_numeric(df["checkout_s"], errors='coerce')

	df["check_out_in_sec_diff"] = (df["checkout_h"]*3600 + df["checkout_m"]*60 + df["checkout_s"]) \
									- (df["checkin_h"]*3600 + df["checkin_m"]*60 + df["checkin_s"])

	return df.loc[df["check_out_in_sec_diff"] >= 0]

def compute_num_work_hours_in_day(df: pd.DataFrame):
	df["num_of_work_hours_in_day"] = df["check_out_in_sec_diff"] / 3600
	return df

def compute_employee_service_length(df: pd.DataFrame):
	df[['date_y', 'date_m', 'date_d']] = df["date"].str.split('-', 3, expand=True)

	return df \
			.join(employees_df.set_index("employee_id"), on="employee_id", how="left") \
			.groupby(["date_m", "date_y", "employee_id"]) \
			.agg({
				'timesheet_id': 'count', 
				'num_of_work_hours_in_day': 'sum', 
				'branch_id': 'mean', 
				'salary': 'mean'}) \
			.reset_index() \
			.rename(columns={
					'date_m': 'work_month',
					'date_y': 'work_year',
					'timesheet_id':'total_work_days_in_month', 
					'num_of_work_hours_in_day': 'total_work_hours_in_month', 
					'branch_id': 'employee_branch_id', 
					'salary': 'employee_salary'})

def compute_salary_per_hour(df: pd.DataFrame):
	salary_per_hour_df = df \
							.groupby(["employee_branch_id", "work_month", "work_year"]) \
							.agg({
								'total_work_hours_in_month': 'sum', 
								'employee_salary': 'sum'}) \
							.reset_index() \
							.rename(columns={
									'total_work_hours_in_month': 'total_work_hours_in_month_all_employees',
									'employee_salary': 'total_employee_salary'})

	salary_per_hour_df["salary_per_hour"] = salary_per_hour_df["total_employee_salary"] \
											/ salary_per_hour_df["total_work_hours_in_month_all_employees"]

	return salary_per_hour_df

def transform_data(employees_df: pd.DataFrame, timesheets_df: pd.DataFrame):
	# filter out records with missing checkin or checkout
	complete_timesheets_df = filter_out_missing_time(timesheets_df)

	# add date to checkin and checkout
	added_date_to_checkin_and_checkout_df = add_date_to_checkin_and_checkout(complete_timesheets_df)
	
	# compute num work hours in day
	num_of_work_hours_in_day_df = compute_num_work_hours_in_day(added_date_to_checkin_and_checkout_df)

	# compute employee service length
	employee_service_length_df = compute_employee_service_length(num_of_work_hours_in_day_df)

	# compute salary per hour
	salary_per_hour_df = compute_salary_per_hour(employee_service_length_df)

	print(salary_per_hour_df)

	return salary_per_hour_df


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
	employees_df = extract_employees_data(EMPLOYEES_DATA, cols=["employee_id", "branch_id", "salary", "join_date", "resign_date"])
	timesheets_df = extract_timesheets_data(TIMESHEETS_DATA, cols=["timesheet_id", "employee_id", "date", "checkin", "checkout"])

	'''
		Transform
	'''
	final_df = transform_data(employees_df, timesheets_df)

	'''
		Load
	'''
	store_data(user=user, db_pass=db_pass, host=host, port=port, db_name=db_name, df=final_df)
