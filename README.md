# Salary per Hour

Please look at `How to Run` section to execute the scripts.

---

## Used Techs

- MySQL 8.0.21
- Python 3.6.5
- Pandas 0.24.2
- sqlalchemy 1.3.22
- mysql-connector-python 8.0.23

---

## Assumptions

- <b>Point 1.</b> The attendance system provides two separate buttons for each work day, one for checking in and the other for checking out. In other words, in case an employee forgot to check out for `day A`, the check in time for `day B` (f.e. one day after `day A`) won't replace the check out time for `day A`.

If <b>Point 1</b> is applied, then the following example does <b>not</b> mean that for work day `2019-09-27`, the check in time is `2019-09-27 07:33:01` and the check out time is `2019-09-28 07:45:46` (because of two separate buttons for each work day).
```
24819929,	41, 	2019-09-27, 	"07:33:01",		NULL
24819930, 	41, 	2019-09-28, 	NULL	  ,		"07:45:46"
```

- <b>Point 2.</b> Both `checkin` and `checkout` time are in the <b>same day</b>. Therefore, such a case where the actual time are`checkin` = `Jan 29, 2021 08:00:00` and `checkout` = `Jan 30, 2021 10:00:00` is assumed to happen on `Jan 29, 2021`.

In addition, such a case where the `checkout` time is less than the `checkin` time will be ignored (f.e. `checkin` = `10:00:00` and `checkout` = `05:00:00`).

- <b>Point 3.</b> When the `salary_per_hour` is `NULL` because of the total work hours is zero, the `NULL` result will still be included in the destination table. There are two additional columns, namely `total_work_hours_in_month_all_employees` and `total_employee_salary` so that the analyst could evaluate in case the `salary_per_hour` is `NULL`.

- <b>Point 4.</b> The definition of `resign_date` is the date when the employee notifies the employer about his/her intent to quit from the job. Therefore, there'll be a notice period between `resign_date` and the last work date (f.e. two weeks notice).
Since there is <b>no</b> any information about the notice period and explicit definition of `resign_date`, the assumption will be applied.
Since this assumption is applied, there is <b>no</b> need to filter out records in `timesheets` whose `date` is above the `resign_date`.

- <b>Point 5.</b> The incremental script will be executed daily at 23:59:59. Therefore, the script will only process data from that day. For example, running the script on `Jan 01, 2021 23:59:59` will extract, transform and load timesheets data with `date` equals to `Jan 01, 2021`.

---

## How Missing Checkin or Checkout is Treated

It's obvious that we can't compute salary per hour when there's missing checkin or checkout.
	
Therefore, all rows with missing checkin or checkout will be filtered out.

Several points to note why this approach is selected:
- <b>Point 1.</b> Filling in the number of hours for missing checkin or checkout with certain statistic (f.e. mean, mode, last recorded num of hours) 
   might yield inaccurate info to the analyst since there are various reasons why the time is missing 
   (f.e. really forgot, trick the system, wanted to check out but forgot because having a talk with co-workers).
- <b>Point 2.</b> Filling in the number of hours for missing checkin or checkout with the default number of hours for the shift (f.e. 8 hours for shift 8.00 to 16.00) is not proper since there is no any information regarding the shift, therefore, doing this action might yield in inaccurate result.
- <b>Point 3.</b> It's important to consider <b>Point 1</b> and <b>Point 2</b> because according to legal law (might be different between countries), the company must still pay the employees for the EXACT amount of work hours.
  Since it requires the exact amount of work hours, the company should find out the missing time by itself.
  This concludes that it does not make sense to go with <b>Point 1</b> and <b>Point 2</b>.
- <b>Point 4.</b> Well yes, different company might have different policy on how to treat missing checkin or checkout.
  However, since this case does not provide any explicit info about the policy, a simple approach (filtering out) is applied.


---

## How to Run

- Make sure you have installed the `Use Techs` in your machine.
- There are two scripts:
  - `full_snapshot.sql`: run daily, <b>read all the data</b> and <b>overwrite</b> the destination table.
      - Go to `prep` folder. There is a runner script called `load.sh`
      - Run `chmod +x load.sh`
      - Run `./load.sh`
      - <b>You will be prompted for password three times</b>
      - The result will be stored to `salary_per_hour_fullsnapshot` table
  - `incremental.py`: run daily, <b>only read the new data</b> and <b>append</b> the result to the destination table.
      - Run `python incremental.py -u <USERNAME> -p <PASSWORD> -ho <HOST> -po <PORT> -db <DB_NAME>`.
      	Default values: `host = localhost`, `port=3306`, `db=salary_per_hour_db`
      - The result will be stored to `salary_per_hour_incremental` table
- What's in `prep` folder?
  - `load.sh`: a runner script for `full_snapshot` mode (create the schema and load the CSV)
  - `load_data.sql`: load the CSV to the created table
  - `schema.sql`: create the database and tables for employees and timesheets data
- Both `full_snapshot` and `incremental` scripts will use the same database
- Both `full_snapshot` and `incremental` scripts will create the following final columns in the destination table: `work_month`, `work_year`, `employee_branch_id`, `total_work_hours_in_month_all_employees`, `total_employee_salary`, and `salary_per_hour`