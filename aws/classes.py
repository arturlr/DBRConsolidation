import json
import sys
import urllib.request, urllib.parse
import boto3
import configparser
import re
from datetime import datetime
from datetime import timedelta


class Athena:
    def __init__(self, key, secret, region, account):
        self.key = key
        self.secret = secret
        self.region = region
        self.account = account
        self.s3bucket = "s3://aws-athena-query-results-%s-%s/" % (account, region)

    def Request(self, query):
        AthenaUrl = "jdbc:awsathena://athena.%s.amazonaws.com:443" % (self.region)
        S3StagingDir = self.s3bucket

        conditionsSetURL = "http://127.0.0.1:10000/query"
        athQuery = {'awsAccessKey': self.key, 'awsSecretKey': self.secret, 'athenaUrl': AthenaUrl,
                    's3StagingDir': S3StagingDir, 'query': query}
        #print(athQuery)
        data = json.dumps(athQuery).encode('utf8')
        req = urllib.request.Request(conditionsSetURL, data=data, headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req)
        jsonresult = json.loads(response.read().decode('utf8'))
        # print(jsonresult)
        return jsonresult


class CloudWatch:
    def __init__(self):
        # self.CW_NAMESPACE = "DBRconsolidation"
        self.CW_NAMESPACE = "DBRTest"
        self.cwclient = boto3.client('cloudwatch')

    def send_metrics(self, dimensions, timestamp, metricname, value, unit):
        metricdata = {'MetricName': metricname, 'Dimensions': dimensions, 'Value': value, 'Unit': unit}
        if timestamp.year == datetime.today().year:
            metricdata['Timestamp'] = timestamp

        # print(MetricData)
        self.cwclient.put_metric_data(
            Namespace=self.CW_NAMESPACE,
            MetricData=[metricdata]
        )

    def get_metrics(self, dimensions, metricname, starttime, endtime, period, stat):
        if len(metricname) < 2:
            print('Invalid MetricName')
            return None

        response = self.cwclient.get_metric_statistics(
            Namespace=self.CW_NAMESPACE,
            MetricName=metricname,
            Dimensions=dimensions,
            StartTime=starttime,
            EndTime=endtime,
            Period=period,
            Unit='None',
            Statistics=[stat]
        )

        return response