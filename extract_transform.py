import logging
import requests
import sys
import send_sns_msg

logger = logging.getLogger()
logger.setLevel(logging.INFO)

auth_list = []
merge_list = []
auth_merged_list = []

def dnld_and_merge(auth_data_url, merge_data_url):
    try:
        logger.info("Attempt to get " + auth_data_url)
        auth_r = requests.get(auth_data_url)
        logger.info("Succeeded to get " + auth_data_url)

        auth_csv_list = auth_r.text.splitlines()
        for auth_csv_line in auth_csv_list:
            auth_tuple = tuple(auth_csv_line.split (","))
            auth_list.append(auth_tuple)

        logger.info("Attempt to get " + merge_data_url)
        merge_r = requests.get(merge_data_url)
        logger.info("Succeeded to get " + merge_data_url)
        merge_csv_list = merge_r.text.splitlines()
        for merge_csv_line in merge_csv_list:
            if "US" in merge_csv_line:
                merge_tuple = tuple(merge_csv_line.split (","))
                merge_list.append(merge_tuple)

        logger.info("Attempt to merge two lists")
        for auth_csv_line in auth_csv_list:
            match = False
            auth_row = auth_csv_line.split (",")
            for merge_csv_line in merge_csv_list:
                if "US" in merge_csv_line:
                    merge_row = merge_csv_line.split (",")
                    if (auth_row[0] == merge_row[0]): # do these rows have the same date
                        match = True
                        #auth_merged_tuple = tuple(auth_row.append(merge_row[6]))
                        #auth_merged_list.append(auth_merged_tuple)
                        auth_row.append(merge_row[6])
                        auth_merged_list.append(tuple(auth_row))
            continue
        logger.info("Succeeded to merge two lists")
        return auth_merged_list

    except Exception as e:
        subject_text = "Extract Transform Module Problem"
        body_text = "Extracting or Transforming data loaded failed due to {}".format(e)
        send_sns_msg.send_notification(subject_text, body_text)
        sys.exit(1)