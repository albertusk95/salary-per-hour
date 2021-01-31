/*
	This script is expected to run daily with full-snapshot mode 
	which means it will read the whole table and overwrite the sink table.
*/

USE salary_per_hour_db;

DROP TABLE IF EXISTS salary_per_hour;

CREATE TABLE salary_per_hour (
	work_month CHAR(2) NOT NULL, 
	work_year CHAR(4) NOT NULL, 
	employee_branch_id INT NOT NULL, 
	total_work_hours_in_month_all_employees DECIMAL(20, 3),
	total_employee_salary DECIMAL(20, 3),
	salary_per_hour DECIMAL(20, 3)
);

INSERT IGNORE INTO salary_per_hour(work_month, work_year, employee_branch_id, total_work_hours_in_month_all_employees, total_employee_salary, salary_per_hour)
WITH complete_timesheets AS (
	SELECT * 
	FROM timesheets 
	WHERE checkin <> '' AND checkout <> ''
), added_date_to_check_in_out_timesheets as ( 
	select cts.*, if(timestampdiff(second, checkin, checkout)<0, STR_TO_DATE(concat(date+INTERVAL 1 DAY, ' ', checkout), '%Y-%m-%d %H:%i:%s'), STR_TO_DATE(concat(date, ' ', checkout), '%Y-%m-%d %H:%i:%s')) as checkout_dt, STR_TO_DATE(concat(date, ' ', checkin), '%Y-%m-%d %H:%i:%s') as checkin_dt 
	from complete_timesheets cts 
), computed_num_work_hours_in_day as (
	select dtts.*, timestampdiff(second, checkin_dt, checkout_dt)/3600 as num_of_work_hours_in_day
	from added_date_to_check_in_out_timesheets dtts
), employee_service_length AS (
	SELECT MONTH(cnwh.date) as work_month, YEAR(cnwh.date) as work_year, emp.salary as employee_salary, emp.branch_id as employee_branch_id, emp.employee_id as employee_id, count(*) as total_work_days_in_month, SUM(cnwh.num_of_work_hours_in_day) as total_work_hours_in_month
	FROM computed_num_work_hours_in_day cnwh 
	LEFT JOIN employees emp 
	ON cnwh.employee_id = emp.employee_id
	GROUP BY MONTH(cnwh.date), YEAR(cnwh.date), emp.employee_id
), salary_per_hour_tmp AS (
	SELECT esl.work_month, esl.work_year, esl.employee_branch_id, SUM(esl.total_work_hours_in_month) as total_work_hours_in_month_all_employees, SUM(esl.employee_salary) as total_employee_salary, SUM(esl.employee_salary) / SUM(esl.total_work_hours_in_month) as salary_per_hour
	FROM employee_service_length esl
	GROUP BY esl.employee_branch_id, esl.work_month, esl.work_year
)
SELECT *
FROM salary_per_hour_tmp;
