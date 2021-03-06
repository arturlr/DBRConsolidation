#!/bin/bash

function run {
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo "$1 errored with $status" >&2
        exit $status
    fi
    return $status
}

ACCESS_KEY=$1
SECRET_KEY=$2

# Creating AWS Config
run sudo mkdir ~/.aws
run printf "[default]\naws_access_key_id=$ACCESS_KEY\naws_secret_access_key=$SECRET_KEY" > ~/credentials
run printf "[default]\nregion=us-east-1\noutput=json" > ~/config
run sudo mv ~/credentials ~/.aws/.
run sudo mv ~/config ~/.aws/.

# Add Drill to PATH
export PATH=/opt/drill/bin:$PATH

UPLOAD_BUCKET=$4

run sudo hostname localhost

# Start Athena Proxy
PORT=10000 java -cp ./athenaproxy/athenaproxy.jar com.getredash.awsathena_proxy.API . &

function convert {

    DATE_SUFFIX=$2

    TEMPDIR="/media/ephemeral0/"
    #TEMPDIR="/temp/"

    ACCTS=$(echo $1 | tr ";" "\n")

    for acct in $ACCTS
    do
        IFS=', ' read -r -a array <<< "$acct"
            if [ "${#array[@]}" -ne 2 ]; then
                echo "Missing parameter for ${acct}"
                continue
            fi
   AWS_ACCOUNT_ID=${array[0]}
   DBR_BUCKET=${array[1]}

   DBRFILES3="s3://${DBR_BUCKET}/${AWS_ACCOUNT_ID}-aws-billing-detailed-line-items-with-resources-and-tags-${DATE_SUFFIX}.csv.zip"
   DBRFILEFS="${AWS_ACCOUNT_ID}-aws-billing-detailed-line-items-with-resources-and-tags-${DATE_SUFFIX}.csv.zip"
   DBRFILEFS_CSV="${AWS_ACCOUNT_ID}-aws-billing-detailed-line-items-with-resources-and-tags-${DATE_SUFFIX}.csv"
   DBRFILEFS_PARQUET="${AWS_ACCOUNT_ID}-aws-billing-detailed-line-items-with-resources-and-tags-${DATE_SUFFIX}.parquet"
   echo "Working on ${AWS_ACCOUNT_ID} for ${DATE_SUFFIX}"

## Assume role to download the files
   run aws sts assume-role --role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/DBRDownload --role-session-name "DBRRole" > ${AWS_ACCOUNT_ID}-assume-role-output.txt

   aws_secret_key=`cat "${AWS_ACCOUNT_ID}-assume-role-output.txt" | grep SecretAccessKey | cut -d':' -f2 | sed 's/[^0-9A-Za-z/+=]*//g'`
   aws_access_key=`cat "${AWS_ACCOUNT_ID}-assume-role-output.txt" | grep AccessKeyId | cut -d':' -f2 | sed 's/[^0-9A-Z]*//g'`
   aws_token_key=`cat "${AWS_ACCOUNT_ID}-assume-role-output.txt" | grep SessionToken | cut -d':' -f2 | sed 's/[^0-9A-Za-z/+=]*//g'`

   export AWS_ACCESS_KEY_ID=${aws_access_key}
   export AWS_SECRET_ACCESS_KEY=${aws_secret_key}
   export AWS_SESSION_TOKEN=${aws_token_key}

## Fetch current DBR file and unzip
   echo "Fetching DBR at $DBRFILES3"
   run aws s3 cp $DBRFILES3 $TEMPDIR
   run unzip -qq $TEMPDIR$DBRFILEFS -d $TEMPDIR

   unset AWS_ACCESS_KEY_ID
   unset AWS_SECRET_ACCESS_KEY
   unset AWS_SESSION_TOKEN

   if [[ ! -f "$TEMPDIR$DBRFILEFS_CSV" ]]; then
      echo 'DBR File does not exist'
      continue
   fi

## Check if DBR file contains Blended / Unblended Rates
    DBR_BLENDED=`head -1 $TEMPDIR$DBRFILEFS_CSV | grep UnBlended | wc -l`

## Column map requried as Athena only works with lowercase columns.
## Also DBR columns are different depending on Linked Account or without hence alter column map based on that
    echo "Converting to Parquet"
    if [ $DBR_BLENDED -eq 1 ]; then
        run ~/DBRConsolidation/csv2parquet.py $TEMPDIR$DBRFILEFS_CSV $TEMPDIR$DBRFILEFS_PARQUET --column-map "InvoiceID" "invoiceid" "PayerAccountId" "payeraccountid" "LinkedAccountId" "linkedaccountid" "RecordType" "recordtype" "RecordId" "recordid" "ProductName" "productname" "RateId" "rateid" "SubscriptionId" "subscriptionid" "PricingPlanId" "pricingplanid" "UsageType" "usagetype" "Operation" "operation" "AvailabilityZone" "availabilityzone" "ReservedInstance" "reservedinstance" "ItemDescription" "itemdescription" "UsageStartDate" "usagestartdate" "UsageEndDate" "usageenddate" "UsageQuantity" "usagequantity" "BlendedRate" "blendedrate" "BlendedCost" "blendedcost" "UnBlendedRate" "unblendedrate" "UnBlendedCost" "unblendedcost" "ResourceId" "resourceid"
    else
       run ~/DBRConsolidation/csv2parquet.py $TEMPDIR$DBRFILEFS_CSV $TEMPDIR$DBRFILEFS_PARQUET --column-map "InvoiceID" "invoiceid" "PayerAccountId" "payeraccountid" "LinkedAccountId" "linkedaccountid" "RecordType" "recordtype" "RecordId" "recordid" "ProductName" "productname" "RateId" "rateid" "SubscriptionId" "subscriptionid" "PricingPlanId" "pricingplanid" "UsageType" "usagetype" "Operation" "operation" "AvailabilityZone" "availabilityzone" "ReservedInstance" "reservedinstance" "ItemDescription" "itemdescription" "UsageStartDate" "usagestartdate" "UsageEndDate" "usageenddate" "UsageQuantity" "usagequantity" "Rate" "rate" "Cost" "cost" "ResourceId" "resourceid"
    fi

## Upload Parquet DBR back to bucket
    echo "uploading to s3://$UPLOAD_BUCKET/dbr-parquet/${AWS_ACCOUNT_ID}-${DATE_SUFFIX}"
    run aws s3 sync /media/ephemeral0/$DBRFILEFS_PARQUET s3://${UPLOAD_BUCKET}/dbr-parquet/${AWS_ACCOUNT_ID}-${DATE_SUFFIX} --quiet

    echo "Athena upload"
    ~/DBRConsolidation/DBRconsolidation.py ${ACCESS_KEY} ${SECRET_KEY} ${UPLOAD_BUCKET} ${AWS_ACCOUNT_ID} ${DBR_BLENDED}

    echo "Cleaning up"
    sudo rm $TEMPDIR$DBRFILEFS
    sudo rm $TEMPDIR$DBRFILEFS_CSV

done

}


DATE_SUFFIX_CURRENT=$(date +%Y-%m)
DATE_SUFFIX_YESTERDAY=$(date -d "-1 days" +%Y-%m)
PAYERSACCOUNTS=$3

convert $PAYERSACCOUNTS $DATE_SUFFIX_CURRENT

echo "Copying html files"
aws s3 cp html/dashcharts.js s3://${UPLOAD_BUCKET}/html/dashcharts.js --acl public-read
aws s3 cp html/DBRdashboard.html s3://${UPLOAD_BUCKET}/html/DBRdashboard.html --acl public-read
aws s3 cp html/aws-sdk-2.45.0.min.js s3://${UPLOAD_BUCKET}/html/aws-sdk-2.45.0.min.js --acl public-read
