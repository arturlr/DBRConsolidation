#!/usr/bin/python3
import json
import sys
import urllib.request, urllib.parse
import boto3
import configparser
import re
import calendar
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import aws.classes


class BuildChartData:
    def __init__(self):
        self.filenamepath = "/media/ephemeral0/"
        self.cw = aws.classes.CloudWatch()

    def get_total_month_to_date(self, payer, cwname, dimensions):
        # Get Month-to-Date payer billing info
        period = 86400
        title = dimensions[len(dimensions)-1]['Value']
        #for i in range(0,len(dimensions)):
        #    title = title + dimensions[i]['Value']
        #    title = title + " - "

        c3_data_arr = [title]
        for f in range(0, 5):
            dtref = datetime.utcnow() - relativedelta(months=+f + 1)
            month = dtref.month
            year = dtref.year
            num_days = calendar.monthrange(year, month)
            startdt = datetime(year, month, 1)
            enddt = datetime(year, month, num_days[1])

            #print(startdt.strftime('%d-%m-%Y'))
            #print(enddt.strftime('%d-%m-%Y'))
            rsp = self.cw.get_metrics(dimensions, cwname, startdt, enddt, period, 'Maximum')
            c3_data_arr.append(self.get_maximum_datapoint(rsp['Datapoints']))

        enddt = datetime.utcnow()
        startdt = datetime(enddt.year, enddt.month, 1)
        rsp = self.cw.get_metrics(dimensions, cwname, startdt, enddt, period, 'Maximum')
        c3_data_arr.append(self.get_maximum_datapoint(rsp['Datapoints']))
        print(c3_data_arr)

    def get_per_hour(self, payer, cwname, dimensions):
        # Get Month-to-Date payer billing info
        period = 600
        title = dimensions[len(dimensions)-1]['Value']
        #for i in range(0,len(dimensions)):
        #    title = title + dimensions[i]['Value']
        #    title = title + " - "

        c3_data_arr = [title]
        c3_x_arr = ['x']
        startdt = datetime.utcnow() - timedelta(days=1)
        enddt = datetime.utcnow()
        rsp = self.cw.get_metrics(dimensions, cwname, startdt, enddt, period, 'Maximum')
        hours_sorted = sorted(rsp['Datapoints'], key=lambda k: k['Timestamp'])

        for h in hours_sorted:
            c3_x_arr.append(h['Timestamp'].strftime('%H-%M'))
            c3_data_arr.append(h['Maximum'])

        print(c3_x_arr)
        print(c3_data_arr)

    def get_maximum_datapoint(self,datapoints):
        maxpt = 0
        for datapt in datapoints:
            cur = datapt['Maximum']
            if cur > maxpt:
                maxpt = cur

        return maxpt



# AWS AccountID
reg = re.compile(r'([0-9]{12})', re.I)

today = datetime.today()
date_suffix_athena = today.strftime("%Y_%m")
date_suffix_bucket = today.strftime("%Y-%m")

if len(sys.argv) != 4:
    print('Invalid arguments. Please use aws_key aws_secret payeraccountid;payeraccountid;...')
    sys.exit(1)

aws_access_key = sys.argv[1]
aws_secret_key = sys.argv[2]
payeraccounts = sys.argv[3].split(';')

#print(payeraccounts)

client = boto3.client("sts", aws_access_key_id=sys.argv[1], aws_secret_access_key=sys.argv[2])
current_account_id = client.get_caller_identity()["Account"]

ath = aws.classes.Athena(aws_access_key, aws_secret_key, "us-east-1", current_account_id)
bch = BuildChartData()

# Getting data and collecting metrics.
for payer in payeraccounts:
    # Total Month-to-Date
    dimensions_arr = [{'Name': 'PayerAccountId', 'Value': payer}]
    response = bch.get_total_month_to_date(payer,'Total Month-to-Date Payer',dimensions_arr)

    response = bch.get_per_hour(payer, 'Total Per Hour Payer', dimensions_arr)

    # Service Month-to-Date
    query = "SELECT DISTINCT productname FROM dbr.autodbr_%s_%s" % (payer,date_suffix_athena)
    rst = ath.Request(query)
    for svc in rst['rows']:
        if svc['productname'] == '':
            continue

        dimensions_arr = [{'Name': 'PayerAccountId', 'Value': payer},
                         {'Name': 'ProductName', 'Value': svc['productname']}]

        response = bch.get_total_month_to_date(payer, 'Services Month-to-Date', dimensions_arr)