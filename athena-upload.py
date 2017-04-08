#!/usr/bin/python3

import boto3
import sys
from pyathenajdbc import connect

conn = connect(s3_staging_dir=sys.argv[1],region_name='us-east-1')
try:
    with conn.cursor() as cursor:
        cursor.execute("""
        create database if not exists dbr
        """)
        print(cursor.description)
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
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
) LOCATION '%s'
TBLPROPERTIES ('has_encrypted_data'='false');
           """ % (sys.argv[2],sys.argv[1])
        else:
           query = """
        create external table if not exists dbr.autodbr_%s_201704 (
        InvoiceID string,
        PayerAccountId string,
        LinkedAccountId string,
        RecordType string,
        RecordId string,
        ProductName string,
        RateId string,
        SubscriptionId string,
        PricingPlanId string,
        UsageType string,
        Operation string,
        AvailabilityZone string,
        ReservedInstance string,
        ItemDescription string,
        UsageStartDate string,
        UsageEndDate string,
        UsageQuantity string,
        BlendedRate string,
        BlendedCost string,
        UnBlendedRate string,
        UnBlendedCost string,
        ResourceId string 
        )
        STORED AS PARQUET
         LOCATION '%s'
           """ % (sys.argv[2],sys.argv[1])
        
        cursor.execute(query)
        print(cursor.description)
finally:
    conn.close()
