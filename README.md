# Salary per Hour

## Used Stack

- MySQL 8.0.21
- Python 3.6.5

---

## Assumptions

- Both `checkin` and `checkout` are in the same day. Therefore, such a case where (`checkin` = Jan 29, 2021 08:00:00 and `checkout` = Jan 30, 2021 10:00:00) does not exist.
- The definition of `resign_date` is the date when the employee notifies the employer about his/her intent to quit from the job. Therefore, there'll be a notice period between `resign_date` and the last work date (f.e. two weeks notice).
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