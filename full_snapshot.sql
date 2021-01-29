# join employee and timesheets to get branch info
WITH employee_service_length AS (
	SELECT MONTH(ts.date) as work_month, YEAR(ts.date) as work_year, emp.salary as employee_salary, branch_id as employee_branch_id, emp.employee_id as employee_id, count(*) as total_work_days
	FROM timesheets ts 
	LEFT JOIN employees emp 
	ON ts.employee_id = emp.employee_id
	GROUP BY MONTH(date), YEAR(date), emp.employee_id
)

SELECT work_month, work_year, employee_branch_id, SUM(employee_salary) / 2, SUM(employee_salary)
FROM employee_service_length 
GROUP BY employee_branch_id, work_month, work_year;

# TODO: replace sum(salary) / 2 with sum(salary) / total_work_hours