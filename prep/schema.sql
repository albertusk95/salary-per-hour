DROP DATABASE IF EXISTS salary_per_hour_db;

CREATE DATABASE salary_per_hour_db;

USE salary_per_hour_db;

CREATE TABLE employees (
	employee_id INT NOT NULL,
	branch_id INT NOT NULL,
	salary DECIMAL(10, 2) NOT NULL,
	join_date DATE NOT NULL,
	resign_date DATE,
	PRIMARY KEY (employee_id)
);

CREATE TABLE timesheets (
	timesheet_id INT NOT NULL,
	employee_id INT NOT NULL,
	date DATE NOT NULL,
	checkin VARCHAR(10),
	checkout VARCHAR(10),
	PRIMARY KEY (timesheet_id)
);