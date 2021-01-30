/*
	This script is expected to run daily with full-snapshot mode which means it will read the whole table and overwrite the sink table.
*/

WITH complete_timesheets AS (
	SELECT * 
	FROM timesheets 
	WHERE checkin <> "" AND checkout <> ""
), employee_service_length AS (
	SELECT MONTH(cts.date) as work_month, YEAR(cts.date) as work_year, emp.salary as employee_salary, emp.branch_id as employee_branch_id, emp.employee_id as employee_id, count(*) as total_work_days, SUM((TIME_TO_SEC(cts.checkout) - TIME_TO_SEC(cts.checkin)) / 3600) as total_work_hours
	FROM complete_timesheets cts 
	LEFT JOIN employees emp 
	ON cts.employee_id = emp.employee_id
	GROUP BY MONTH(date), YEAR(date), emp.employee_id
)

SELECT work_month, work_year, employee_branch_id, SUM(employee_salary) / SUM(total_work_hours) as salary_per_hour
FROM employee_service_length 
GROUP BY employee_branch_id, work_month, work_year;
