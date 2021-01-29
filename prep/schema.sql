DROP DATABASE IF EXISTS salary_per_hour;

CREATE DATABASE salary_per_hour;

USE salary_per_hour;

CREATE TABLE employees (
	employee_id INT NOT NULL,
	branch_id INT NOT NULL,
	salary DECIMAL(10, 2) NOT NULL,
	join_date DATE NOT NULL,
	resign_date DATE NULL,
	PRIMARY KEY (employee_id)
);

CREATE TABLE timesheets (
	timesheet_id INT NOT NULL,
	employee_id INT NOT NULL,
	date DATE NOT NULL,
	checkin CHAR(8) NULL ,
	checkout CHAR(8) NULL,
	PRIMARY KEY (timesheet_id)
);
