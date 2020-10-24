Event-Driven Python ETL on AWS
------------------------------

This repository contains a Python compute job that runs on a daily schedule triggered it from a once-daily CloudWatch rule.

EXTRACTION
----------
The Python code downloads a CSV file from Github which contains a daily dump of US COVID-19 data from a repository maintained by the New York Times. Every day, the file updates with an additional row of data.

TRANSFORMATION
--------------
Cleaning – The date field is converted to a date object, not a string.
Joining – We want to show recovered cases as well as confirmed cases and deaths. The NYT data does not track recoveries, so need to pull US recovery data from a Johns Hopkins dataset and merge it into the NYT data for each day. (Note: the case and death counts for the Johns Hopkins dataset disagree with the NYT data and, so, we treat the NYT data as authoritative and only copy the recovery data from Johns Hopkins.)
Filtering – Remove non-US data from the Johns Hopkins dataset. Remove any days that do not exist in both datasets. (There is an off-by-one issue.)

CODE CLEANUP - Abstracted the data manipulation work into a Python module. This module only performs transformations. It does not care where the CSV files are stored and it knows nothing about the database in the next step.

LOAD
----
Transformed data is written into a RDS MySQL database.  Each record in the table has the date, US case count, deaths, and recoveries for a day of the pandemic.

NOTIFICATION
------------
When the database has been updated, the code triggers a SNS message to notify any interested consumers that the ETL job has completed. The message includes the number of rows updated in the database.

ERROR HANDLING
--------------
The code handles these common control flow situations:

Initial load vs update — you should be able to load the entire historical data set into your database the first time the job is run, and then update with only the most recent day’s data thereafter.
If the data contains unexpected or malformed input, your code should fail gracefully and report an error message via SNS. Next time your job runs, it should remember that it did not succeed in processing the previous data, and try again before moving on to more recent data.

TESTS
-----
To ensure that your code can handle unexpected situations, include unit tests for your code that substitute invalid data for the COVID-19 CSV files, and confirm that your code responds correctly.

Infrasturture As Code (IaC)
---------------------------
All infrastructure (Lambda function, CloudWatch rule, SNS trigger, database, etc) is defined in code CloudFormation (lambda-rds-vpc.yaml).

DASHBOARD
---------
What would an ETL process be without a report? Therefore, database is hooked up to AWS Quicksight to generate a visualization of US case counts, fatality, and recoveries over time (quicksightimage.png).
