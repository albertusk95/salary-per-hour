USE salary_per_hour_db;

LOAD DATA LOCAL INFILE '../data/employees.csv' 
INTO TABLE employees 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '../data/timesheets.csv' 
INTO TABLE timesheets 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;