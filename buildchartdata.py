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


class BuildChartData:
    def __init__(self):
        self.filenamepath = "/media/ephemeral0/"
        self.cw = aws.classes.CloudWatch()

    def gethourinfoperpayer(self, payer):

        # Get Month-to-Date payer billing info
        dimensionsArr = [{'Name' : 'PayerAccountId',
                          'Value': payer}]

        rsp = self.cw.get_metrics(dimensionsArr, 'Total Month-to-Date Payer', 'monthly')
        print(rsp)

        # Get Per Hour payer billing info
        dimensionsArr = [{'Name' : 'PayerAccountId',
                          'Value' : payer}]
        rsp = self.cw.get_metrics(dimensionsArr, 'Total Per Hour Payer', 'hourly')
        print(rsp)


# Initializing Variables
config = configparser.ConfigParser()
config.read('DBRconsolidation.ini')

# AWS AccountID
reg = re.compile(r'([0-9]{12})', re.I)

today = datetime.today()
date_suffix_athena = today.strftime("%Y_%m")
date_suffix_bucket = today.strftime("%Y-%m")

if len(sys.argv) != 3:
    print('Invalid arguments. Please use aws_key aws_secret payeraccountid;payeraccountid;...')
    sys.exit(1)

aws_access_key = sys.argv[1]
aws_secret_key = sys.argv[2]
payeraccounts = sys.argv[3].split(';')

client = boto3.client("sts", aws_access_key_id=sys.argv[1], aws_secret_access_key=sys.argv[2])
current_account_id = client.get_caller_identity()["Account"]

ath = aws.classes.Athena(aws_access_key, aws_secret_key, "us-east-1", current_account_id)
bch = BuildChartData()

# Getting data and collecting metrics.
for sec in config.sections():
    if sec.lower().startswith("accountmetric"):
        cwName = config[sec]['name']
        print('Starting ' + cwName)
        if config[sec]['enabled'].lower() != 'true':
            print('Not processing ' + cwName)
            continue

        for payer in payeraccounts:
            if 'per hour' in cwName.lower():
                response = bch.gethourinfoperpayer(payer)


