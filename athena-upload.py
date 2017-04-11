#!/usr/bin/python3
import json
import sys
import urllib.request, urllib.parse
import boto3

class Athena:
    def __init__(self,key,secret,region,account):
        self.key = key
        self.secret = secret
        self.region = region
        self.account = account
        self.s3bucket = "aws-athena-query-results-%s-%s" % (account,region)
        print(self.s3bucket)


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


aws_access_key = sys.argv[1]
aws_secret_key = sys.argv[2]
upload_bucket = sys.argv[3]
date_suffix = sys.argv[4]
dbr_blended = sys.argv[5]

client = boto3.client("sts", aws_access_key_id=sys.argv[1], aws_secret_access_key=sys.argv[2])
account_id = client.get_caller_identity()["Account"]

ath = Athena(aws_access_key,aws_secret_key,"us-east-1",account_id)
ath.Request("create database if not exists dbr")

if (dbr_blended == 0):
    query = """
    CREATE EXTERNAL TABLE IF NOT EXISTS dbr.autodbr_%s_%s (
      `invoiceid` string,
      `payeraccountid` string,
      `linkedaccountid` string,
      `recordtype` string,
      `recordid` string,
      `productname` string,
      `rateid` string,
      `subscriptionid` string,
      `pricingplanid` string,
      `usagetype` string,
      `operation` string,
      `availabilityzone` string,
      `reservedinstance` string,
      `itemdescription` string,
      `usagestartdate` string,
      `usageenddate` string,
      `usagequantity` string,
      `rate` string,
      `cost` string,
      `resourceid` string
    )
    STORED AS PARQUET
    LOCATION 's3://%s/dbr-parquet/%s-%s/'
    """ % (account_id,date_suffix,upload_bucket,account_id,date_suffix)
else:
    query = """
    create external table if not exists `dbr.autodbr_%s_%s` (
    `InvoiceID` string,
    `PayerAccountId` string,
    `LinkedAccountId` string,
    `RecordType` string,
    `RecordId` string,
    `ProductName` string,
    `RateId` string,
    `SubscriptionId` string,
    `PricingPlanId` string,
    `UsageType` string,
    `Operation` string,
    `AvailabilityZone` string,
    `ReservedInstance` string,
    `ItemDescription` string,
    `UsageStartDate` string,
    `UsageEndDate` string,
    `UsageQuantity` string,
    `BlendedRate` string,
    `BlendedCost` string,
    `UnBlendedRate` string,
    `UnBlendedCost` string
    )
    STORED AS PARQUET
    LOCATION 's3://%s/dbr-parquet/%s-%s/'
    """ % (account_id,date_suffix,upload_bucket,account_id,date_suffix)

ath.Request(query)

