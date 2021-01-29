# Each command prompts for a password, executes the given command, and returns to the shell (no logout required).

# import schema
/usr/local/mysql-8.0.21-macos10.15-x86_64/bin/mysql -h localhost -u root -p < schema.sql

# set up the local infile
/usr/local/mysql-8.0.21-macos10.15-x86_64/bin/mysql -h localhost -u root -p --execute="SET GLOBAL local_infile=1;"

# load the csv
/usr/local/mysql-8.0.21-macos10.15-x86_64/bin/mysql --local-infile=1 -h localhost -u root -p -e 'source load_data.sql'