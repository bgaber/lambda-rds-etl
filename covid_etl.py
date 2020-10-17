import sys
import logging
import os
import pymysql
import datetime
import extract_transform
import send_sns_msg

db_host  = os.environ['dbEndpoint']
name     = os.environ['dbUsername']
password = os.environ['dbPassword']
db_name  = os.environ['dbName']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(db_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance - " + db_host + ".  Check Security Group")
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
def lambda_handler(event, context):
    auth_merged_list = []

    # CSV Column Names
    # date,cases,deaths
    auth_data_url = "https://github.com/nytimes/covid-19-data/raw/master/us.csv"

    # CSV Column Names
    # Date,Country/Region,Province/State,Lat,Long,Confirmed,Recovered,Deaths
    merge_data_url = "https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv"

    auth_merged_list = extract_transform.dnld_and_merge(auth_data_url, merge_data_url)

    with conn.cursor() as cur:
        cur.execute("create table if not exists covid_merged_data (id INT UNSIGNED NOT NULL AUTO_INCREMENT, cdate date DEFAULT NULL, cases INT UNSIGNED NOT NULL, deaths INT UNSIGNED NOT NULL, recovered INT UNSIGNED NOT NULL, PRIMARY KEY (id))")
        conn.commit()
        cur.execute("select count(*) as num_rows from covid_merged_data")
        record = cur.fetchone()
        if (record[0] == 0):
            sql = "INSERT INTO covid_merged_data (cdate,cases,deaths,recovered) VALUES (%s, %s, %s, %s)"
            cur.executemany(sql, auth_merged_list)
            #for auth_merged_row in auth_merged_list:
            #    date,cases,deaths,recovered=auth_merged_row
            #    cur.execute('insert into covid_merged_data (cdate,cases,deaths,recovered) values(%s, %s, %s, %s)', auth_merged_row)
            conn.commit()
        else:
            cur.execute("select max(cdate) as most_recent_date from covid_merged_data")
            record = cur.fetchone()
            # print(type(record[0])) # this will output <class 'datetime.date'>
            db_time_obj = record[0]
            #db_time_obj = datetime.datetime.strptime(record[0], '%Y-%m-%d')
            for auth_merged_row in auth_merged_list:
                aml_time_obj = datetime.datetime.strptime(auth_merged_row[0], '%Y-%m-%d')
                #print(type(aml_time_obj.date())) # this will output <class 'datetime.datetime'>
                if (aml_time_obj.date() > db_time_obj):
                    print("Inserting new row with date of {0}".format(aml_time_obj))
                    cur.execute('insert into covid_merged_data (cdate,cases,deaths,recovered) values(%s, %s, %s, %s)', auth_merged_row)
                    conn.commit()
        logger.info("Successful run of the Python Covid ETL Lambda Function")
        subject_text = "Successful run of the Covid ETL Lambda Function"
        body_text = "If new Covid data was found it has been loaded into the database."
        send_sns_msg.send_notification(subject_text, body_text)
    return "Successful run of the Python Covid ETL program"
