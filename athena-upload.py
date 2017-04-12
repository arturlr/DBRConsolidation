#!/usr/bin/python3
import json
import sys
import urllib.request, urllib.parse
import boto3
import configparser
import configparser
from datetime import date


class Athena:
    def __init__(self,key,secret,region,account):
        self.key = key
        self.secret = secret
        self.region = region
        self.account = account
        self.s3bucket = "s3://aws-athena-query-results-%s-%s/" % (account,region)


    def Request(self,query):
        AthenaUrl = "jdbc:awsathena://athena.%s.amazonaws.com:443" % (self.region)
        S3StagingDir = self.s3bucket

        conditionsSetURL = "http://127.0.0.1:10000/query"
        athQuery={'awsAccessKey': self.key,'awsSecretKey': self.secret,'athenaUrl': AthenaUrl,'s3StagingDir': S3StagingDir,'query': query}
        print(athQuery)
        data = json.dumps(athQuery).encode('utf8')
        req = urllib.request.Request(conditionsSetURL,data=data,headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req)
        print(response.read().decode('utf8'))


# Initializing Variables
config = configparser.ConfigParser()
config.read('DBRconsolidation.ini')

today = date.today()
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
ath = Athena(aws_access_key,aws_secret_key,"us-east-1",current_account_id)

query = config['athena']['dbrCreation']
ath.Request(query)

if (dbr_blended == 0):
    query = config['athena']['dbrTable']
else:
    query = config['athena']['dbrBlendedTable']

query = query.replace("**BUCKET**",upload_bucket)
query = query.replace("**ACCT**",dbr_account_id,2)
query = query.replace("**DATEBUCKET**",date_suffix_bucket)
query = query.replace("**DATETABLE**",date_suffix_athena)
ath.Request(query)

# Getting data and collecting metrics

