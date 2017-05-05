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
    def __init__(self,access_key,secret_key,bucket):
        self.filenamepath = "/media/ephemeral0/"
        self.cw = aws.classes.CloudWatch()
        self.date_suffix_athena = datetime.now().strftime("%Y_%m")
        self.bucket = bucket

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
            dt_ref = datetime.utcnow() - relativedelta(months=f)
            month = dt_ref.month
            year = dt_ref.year
            dt_start = datetime(year, month, 1)
            c3_data[c3_data_index]['x'].append(dt_start.strftime('%m-%Y'))

        for payer in payeraccounts:
            dimensions_arr = [{'Name': 'PayerAccountId', 'Value': payer}]
            c3_data.append({payer: [payer]})
            c3_data_index = c3_data_index + 1

            for f in range(5,0,-1):
                dt_ref = datetime.utcnow() - relativedelta(months=f)
                month = dt_ref.month
                year = dt_ref.year
                num_days = calendar.monthrange(year, month)
                dt_start = datetime(year, month, 1)
                dt_end = datetime(year, month, num_days[1])

                rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
                c3_data[c3_data_index][payer].append(self.get_maximum_datapoint(rsp['Datapoints']))

            dt_end = datetime.utcnow()
            dt_start = datetime(dt_end.year, dt_end.month, 1)
            rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
            c3_data[c3_data_index][payer].append(self.get_maximum_datapoint(rsp['Datapoints']))

        return c3_data


    def get_services(self, payeraccounts, metric_name, duration):
        list_svc = []

        c3_data = [{'x': ['x']}]
        c3_data_index = 0

        if duration == 'daily':
            period = 86400
            dt_end = datetime.utcnow()
            dt_start = dt_end - relativedelta(months=1)
            # Populate with the date range
            for f in range(29,0,-1):
                dt_ref = datetime.utcnow() - relativedelta(days=f)
                month = dt_ref.month
                year = dt_ref.year
                c3_data[c3_data_index]['x'].append(dt_ref.strftime('%Y-%m-%d'))

        else:
            period = 600
            dt_end = datetime.utcnow()
            dt_start = datetime.utcnow() - timedelta(days=1)
            # Populate with the date range
            for f in range(23,0,-1):
                dt_ref = datetime.utcnow() - relativedelta(hours=f)
                c3_data[c3_data_index]['x'].append(dt_ref.strftime('%H-%M'))

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

                rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
                if len(rsp['Datapoints']) == 0:
                    continue

                c3_data.append({payer + '-' + svc: [payer + '-' + svc]})
                c3_data_index = c3_data_index + 1

                if duration == 'daily':
                    rangepoints = 29
                    time_format = '%Y-%m-%d'
                else:
                    rangepoints = 23
                    time_format = '%H-%M'


                hours_sorted = sorted(rsp['Datapoints'], key=lambda k: k['Timestamp'])
                for h in hours_sorted:
                    for f in range(rangepoints,0,-1):
                        if duration == 'daily':
                            dt_ref = datetime.utcnow() - relativedelta(days=f)
                        else:
                            dt_ref = datetime.utcnow() - relativedelta(months=f)
                        month = dt_ref.month
                        year = dt_ref.year
                        if dt_ref.strftime('%Y-%m-%d') == h['Timestamp'].strftime(time_format):
                            c3_data[c3_data_index][payer + '-' + svc].append(h['Maximum'])
                            break
                        else:
                            c3_data[c3_data_index][payer + '-' + svc].append(0)

        return c3_data


    def get_per_hour(self, payeraccounts, metric_name):
        period = 600

        c3_data_hour = [{'x': ['x']}]
        c3_data_hour_index = 0
        dt_ref = datetime.utcnow()
        # Populate with the date range
        for f in range(24, -1, -1):
            dt = dt_ref - timedelta(hours=f)
            c3_data_hour[c3_data_hour_index]['x'].append(dt.isoformat() + 'Z')

        for payer in payeraccounts:
            c3_data_hour.append({payer: [payer]})
            c3_data_hour_index = c3_data_hour_index + 1

            dimensions_arr = [{'Name': 'PayerAccountId', 'Value': payer}]
            dt_start = datetime.utcnow() - timedelta(days=1)
            dt_end = datetime.utcnow()
            rsp = self.cw.get_metrics(dimensions_arr, metric_name, dt_start, dt_end, period, 'Maximum')
            hours_sorted = sorted(rsp['Datapoints'], key=lambda k: k['Timestamp'])

            # Parse the metrics ans populate the values
            for f in range(24, -1, -1):
                dt = dt_ref - timedelta(hours=f)
                flag_found = False
                for dp in hours_sorted:
                    if dp['Timestamp'].hour == dt.hour and dp['Timestamp'].day == dt.day:
                        c3_data_hour[c3_data_hour_index][payer].append(dp['Maximum'])
                        # print(payer + ' : ' + dt.strftime('%x-%X') + ' - ' + str(dp['Maximum']))
                        flag_found = True
                        break
                if flag_found == False:
                    c3_data_hour[c3_data_hour_index][payer].append(0)
                    # print(payer + ' : ' + dt.strftime('%x-%X') + ' - ' + '0')

        return c3_data_hour


    def get_maximum_datapoint(self,datapoints):
        maxpt = 0
        for datapt in datapoints:
            cur = datapt['Maximum']
            if cur > maxpt:
                maxpt = cur

        return maxpt


    def format_c3_json(self, file_name, values_array):
        print(file_name)
        body = ""
        for values in values_array:
            for k, v in values.items():
                count = 0
                for i in v:
                    if count == 0:
                        body = body + '["' + str(k) + '",'
                    elif count == len(v) - 1:
                        if (k == "x"):
                            body = body + '"' + str(i) + '"],'
                        else:
                            body = body + str(i) + '],'
                    else:
                        if (k == "x"):
                            body = body + '"' + str(i) + '",'
                        else:
                            body = body + str(i) + ','

                    count = count + 1
        body = body[:-1]

        with open(self.filenamepath + file_name +  ".json", "w") as text_file:
            print(body, file=text_file)

        s3 = boto3.client('s3')
        s3.upload_file(self.filenamepath + file_name + ".json", self.bucket, "html/" + file_name + ".txt")
        print(body)


###################################
#
# Initialize Variable

payeraccounts = sys.argv[3].split(';')

bch = BuildChartData(sys.argv[1],sys.argv[2],sys.argv[4])

###################################
#
# Obtain Data and Creating the report arrays

metric_name = 'Estimate Month-to-Date Payer'
response = bch.get_last_6_month_to_date(payeraccounts,metric_name)
c3_data = [{metric_name: response }]

metric_name = 'Estimate Per Hour Payer'
response = bch.get_per_hour(payeraccounts,metric_name)
c3_data.append({metric_name:response})

metric_name = 'Estimate Services Per Hour Payer'
response = bch.get_services(payeraccounts, metric_name,'daily')
c3_data.append({metric_name:response})

metric_name = 'Estimate Services Per Hour Payer'
response = bch.get_services(payeraccounts, metric_name,'hourly')
c3_data.append({metric_name:response})

for item in c3_data:
    for metric_name, values_array in item.items():
        if values_array == None:
            continue
        file_name = metric_name.replace(" ", "_").lower()
        file_name = file_name.replace("-", "_")
        bch.format_c3_json(file_name, values_array)

#print(c3_data)