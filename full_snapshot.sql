/*
	It's obvious that we can't compute salary per hour when there's missing checkin or checkout.
	
	Therefore, all rows with missing checkin or checkout will be filtered out.

	Several points to note why this approach is chosen:
	1) Filling in the number of hours for missing checkin or checkout with certain statistic (f.e. mean, mode, last recorded num of hours) 
	   might yield inaccurate info to the analyst since there are various reasons why the time is missing 
	   (f.e. really forgot, trick the system, wanted to check out but forgot because having a talk with co-workers).

	2) Filling in the number of hours for missing checkin or checkout with the default number of hours for the shift (f.e. 8 hours for shift 8.00 to 16.00)
	   is not proper since there is no any information regarding the shift, therefore, doing this action might yield in inaccurate result.

	3) Point (1) and (2) are important because according to legal law (might be different between countries), 
	   the company must still pay the employees for the EXACT amount of work hours. 
	   Since it requires the exact amount of work hours, the company should find out the missing time by itself.
	   
	   This concludes that it does not make sense to go with point (1) and (2).

	4) Well yes, different company might have different policy on how to treat missing checkin or checkout.
	   However, since this case does not provide any explicit info about the policy, a simple approach (filtering out) is applied.
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

SELECT work_month, work_year, employee_branch_id, SUM(employee_salary) / SUM(total_work_hours), SUM(employee_salary)
FROM employee_service_length 
GROUP BY employee_branch_id, work_month, work_year;
