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
        Rate string,
        Cost string
        )
        STORED AS PARQUET
         LOCATION '%s'
        """ % (sys.argv[2],sys.argv[1])
        print(query)
        cursor.execute(query)
        print(cursor.description)
finally:
    conn.close()
