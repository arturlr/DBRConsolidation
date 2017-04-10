#!/usr/bin/python3
import json
import sys
import urllib.request, urllib.parse

class Athena:
    def __init__(self,key,secret,region,account):
        self.key = key
        self.secret = secret
        self.region = region
        self.account = account


    def Request(self,query):
        AthenaUrl = "jdbc:awsathena://athena.%s.amazonaws.com:443" % (self.region)
        S3StagingDir= "s3://%s/%s" % (sys.argv[3],self.account)

        conditionsSetURL = "http://127.0.0.1:10000/query"
        athQuery={'awsAccessKey': self.key,'awsSecretKey': self.secret,'athenaUrl': AthenaUrl,'s3StagingDir': S3StagingDir,'query': query}
        data = json.dumps(athQuery).encode('utf8')
        req = urllib.request.Request(conditionsSetURL,data=data,headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req)
        print(response.read().decode('utf8'))



ath = Athena("AKIAIZUDOT73KMDKL2QA","ptVurpkOaaB4y0S4X/OStqLIAPnG33Z1BEqC13gO","us-east-1","514046899996")

ath.Request("create database if not exists dbr")

if (sys.argv[3] == 0):
    query = """
    CREATE EXTERNAL TABLE IF NOT EXISTS dbr.autodbr_%s_201704 (
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
    STORED AS PARQUET;
    """ % (sys.argv[2],sys.argv[1])
else:
    query = """
    create external table if not exists `dbr.autodbr_%s_201704` (
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
    """ % (sys.argv[2],sys.argv[1])

ath.Request(query)

