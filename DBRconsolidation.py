#!/usr/bin/python3
import json
import sys
import urllib.request, urllib.parse
import boto3
import configparser
import re
from datetime import datetime
from datetime import timedelta
import aws.classes


# Initializing Variables
config = configparser.ConfigParser()
config.read('DBRconsolidation.ini')

# AWS AccountID
reg = re.compile(r'([0-9]{12})', re.I)

today = datetime.today()
date_suffix_athena = today.strftime("%Y_%m")
date_suffix_bucket = today.strftime("%Y-%m")

aws_access_key = sys.argv[1]
aws_secret_key = sys.argv[2]
upload_bucket = sys.argv[3]
dbr_account_id = sys.argv[4]
dbr_blended = int(sys.argv[5])

client = boto3.client("sts", aws_access_key_id=sys.argv[1], aws_secret_access_key=sys.argv[2])
current_account_id = client.get_caller_identity()["Account"]

# Initializating Athena
ath = aws.classes.Athena(aws_access_key, aws_secret_key, "us-east-1", current_account_id)

if dbr_blended == 0:
    query = config['athena']['dbrTable']
    cost_column = 'cost'
else:
    query = config['athena']['dbrBlendedTable']
    cost_column = 'blendedcost'

query = query.replace("**BUCKET**", upload_bucket)
query = query.replace("**ACCT**", dbr_account_id, 2)
query = query.replace("**DATEBUCKET**", date_suffix_bucket)
query = query.replace("**DATETABLE**", date_suffix_athena)
ath.Request(query)

cw = aws.classes.CloudWatch()

# Getting data and collecting metrics.
for sec in config.sections():
    if sec.lower().startswith("accountmetric"):
        cwName = config[sec]['name']
        print('Starting ' + cwName)
        if config[sec]['enabled'].lower() != 'true':
            print('Not processing ' + cwName)
            continue

        sqlQuery = config[sec]['sqlQuery']
        sqlQuery = sqlQuery.replace("**COST**", cost_column, 2)
        sqlQuery = sqlQuery.replace("**ACCT**", dbr_account_id, 2)
        sqlQuery = sqlQuery.replace("**DATETABLE**", date_suffix_athena, 2)
        rsp = ath.Request(sqlQuery)

        for row in rsp['rows']:
            if 'value' not in row:
                continue

            # for CloudWatch dimensions key-pair value
            dimArray = [{'Name': 'PayerAccountId',
                        'Value': dbr_account_id}]

            value = round(float(row['value']), 5)

            if 'date' in row:
                dt = datetime.strptime(row['date'] + ':0:0', "%Y-%m-%d %H:%M:%S")
            else:
                dt = datetime(1900, 1, 1)

            if 'linkedaccountid' in row:
                rst = reg.findall(row['linkedaccountid'])  # Check AccountId has 12 digitis
                if rst:
                    dimArray.append({'Name': 'LinkedAccountId',
                                     'Value': row['linkedaccountid']})

            if 'productname' in row:
                if row['productname'] != '':
                    dimArray.append({'Name': 'ProductName',
                                     'Value': row['productname']})

            cw.send_metrics(dimArray, dt, cwName, value, 'None')
