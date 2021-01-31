# Salary per Hour

## Used Techs

- MySQL 8.0.21
- Python 3.6.5
- Pandas 0.24.2

---

## Assumptions

- <b>Point 1.</b> The attendance system provides two separate buttons for each work day, one for checking in and the other for checking out. In other words, in case an employee forgot to check out for `day A`, the check in time for `day B` (f.e. one day after `day A`) won't replace the check out time for `day A`.

If <b>Point 1</b> is applied, then the following example does <b>not</b> mean that for work day `2019-09-27`, the check in time is `2019-09-27 07:33:01` and the check out time is `2019-09-28 07:45:46` (because of two separate buttons for each work day).
```
24819929,	41, 	2019-09-27, 	"07:33:01",		NULL
24819930, 	41, 	2019-09-28, 	NULL	  ,		"07:45:46"
```

- <b>Point 2.</b> Both `checkin` and `checkout` time are in the same day. Therefore, such a case where (`checkin` = `Jan 29, 2021 08:00:00` and `checkout` = `Jan 30, 2021 10:00:00`) does <b>not</b> exist.
Basically, it's difficult to know the actual number of work hours when the date is not specified. For example, one can record `checkin` at `09:00:00` and `checkout` at `17:00:00`. However, we can't know date on which each `checkin` and `checkout` is recorded. For example, the `checkin` might be recorded on `2019-03-03`, while the `checkout` might be recorded on `2019-03-03`, `2019-03-04`, or `2019-03-05`.

The date needs to be considered since it affects the total work hours.

- <b>Point 3.</b> When the `salary_per_hour` is `NULL` because of the total work hours is zero, the `NULL` result will still be included in the destination table. There are two additional columns, namely `total_work_hours` and `total_employee_salary` so that the analyst could evaluate in case the `salary_per_hour` is `NULL`.

- <b>Point 4.</b> The definition of `resign_date` is the date when the employee notifies the employer about his/her intent to quit from the job. Therefore, there'll be a notice period between `resign_date` and the last work date (f.e. two weeks notice).
Since there is <b>no</b> any information about the notice period and explicit definition of `resign_date`, the assumption will be applied.
Since this assumption is applied, there is <b>no</b> need to filter out records in `timesheets` whose `date` is above the `resign_date`.

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

Number of rows in `timesheets` = 39714. `select count(*) from timesheets where date is not null;` gives 39714.
`select count(*) from timesheets where date+INTERVAL 1 DAY is not null;` returns 39714.
