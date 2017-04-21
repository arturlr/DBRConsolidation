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
    def __init__(self,access_key,secret_key):
        self.filenamepath = "/media/ephemeral0/"
        self.cw = aws.classes.CloudWatch()
        self.date_suffix_athena = datetime.now().strftime("%Y_%m")

        client = boto3.client("sts", aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        current_account_id = client.get_caller_identity()["Account"]
        self.ath = aws.classes.Athena(access_key, secret_key, "us-east-1", current_account_id)

    def get_last_6_month_to_date(self, payer_accounts, metric_name):
        # Get Month-to-Date payer billing info
        period = 86400

        c3_data = [{'x': ['x']}]
        c3_data_index = 0

        # Populate with the date range
        for f in range(5,-1,-1):
            dt_ref = datetime.utcnow() - relativedelta(months=+f + 1)
            month = dt_ref.month
            year = dt_ref.year
            dt_start = datetime(year, month, 1)
            c3_data[c3_data_index]['x'].append(dt_start.strftime('%m-%Y'))

        for payer in payeraccounts:
            dimensions_arr = [{'Name': 'PayerAccountId', 'Value': payer}]
            c3_data.append({'data': [payer]})
            c3_data_index = c3_data_index + 1

            for f in range(5,0,-1):
                dt_ref = datetime.utcnow() - relativedelta(months=+f + 1)
                month = dt_ref.month
                year = dt_ref.year
                num_days = calendar.monthrange(year, month)
                dt_start = datetime(year, month, 1)
                dt_end = datetime(year, month, num_days[1])

                rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
                c3_data[c3_data_index]['data'].append(self.get_maximum_datapoint(rsp['Datapoints']))

            dt_end = datetime.utcnow()
            dt_start = datetime(dt_end.year, dt_end.month, 1)
            rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
            c3_data[c3_data_index]['data'].append(self.get_maximum_datapoint(rsp['Datapoints']))

        return c3_data


    def get_services(self, payer_account, metric_name, range):
        if range == 'daily':
            period = 86400
            dt_end = datetime.utcnow()
            dt_start = datetime(dt_end.year, dt_end.month, 1)
        else:
            period = 600
            dt_end = datetime.utcnow()
            dt_start = datetime.utcnow() - timedelta(days=1)

        list_svc = []

        c3_data = [{'x': ['x']}]
        c3_data_index = 0

        # Consolidating all the services into one list
        for payer in payeraccounts:
            query = "SELECT DISTINCT productname FROM dbr.autodbr_%s_%s" % (payer, self.date_suffix_athena)
            rst = self.ath.Request(query)
            for s in rst['rows']:
                if s['productname'] == '':
                    continue
                if s['productname'] not in list_svc:
                    list_svc.append(s['productname'])

        for payer in payeraccounts:
            for svc in list_svc:
                dimensions_arr = [{'Name': 'PayerAccountId', 'Value': payer},
                                  {'Name': 'ProductName', 'Value': svc}]

                if range == 'daily':
                    rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
                else:
                    rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
                    hours_sorted = sorted(rsp['Datapoints'], key=lambda k: k['Timestamp'])

                    for h in hours_sorted:
                        c3_data[0]['x'].append(h['Timestamp'].strftime('%H-%M'))
                        c3_data[c3_data_index]['data'].append(h['Maximum'])


    def get_per_hour(self, payer_accounts, metric_name):
        period = 600

        c3_data_hour = [{'x': ['x']}]
        c3_data_hour_index = 0
        for payer in payeraccounts:
            c3_data_hour.append({'data': [payer]})
            c3_data_hour_index = c3_data_hour_index + 1

            dimensions_arr = [{'Name': 'PayerAccountId', 'Value': payer}]
            dt_start = datetime.utcnow() - timedelta(days=1)
            dt_end = datetime.utcnow()
            rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
            hours_sorted = sorted(rsp['Datapoints'], key=lambda k: k['Timestamp'])

            for dp in hours_sorted:
                c3_data_hour[0]['x'].append(dp['Timestamp'].strftime('%H-%M'))
                c3_data_hour[c3_data_hour_index]['data'].append(dp['Maximum'])

        return c3_data_hour

    def get_maximum_datapoint(self,datapoints):
        maxpt = 0
        for datapt in datapoints:
            cur = datapt['Maximum']
            if cur > maxpt:
                maxpt = cur

        return maxpt

###################################
#
# Initialize Variable

if len(sys.argv) != 4:
    print('Invalid arguments. Please use aws_key aws_secret payeraccountid;payeraccountid;...')
    sys.exit(1)


payeraccounts = sys.argv[3].split(';')

bch = BuildChartData(sys.argv[1],sys.argv[2])

###################################
#
# Obtain Data and Creating the report arrays

metric_name = 'Estimate Month-to-Date Payer'
response = bch.get_last_6_month_to_date(payeraccounts,metric_name)
c3_data = [{metric_name: response }]

metric_name = 'Estimate Per Hour Payer'
response = bch.get_per_hour(payeraccounts,metric_name)
c3_data.append({metric_name:response})

metric_name = 'Estimate Month-to-Date Services'
response = bch.get_services(payeraccounts, metric_name,'daily')
c3_data.append({metric_name:response})

print(c3_data)



