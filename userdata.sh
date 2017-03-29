#!/bin/bash

# INSTALL PRE-REQS
sudo yum update -y
sudo chmod 777 /media/ephemeral0/
sudo yum install -y git
sudo mkdir /opt/drill
sudo mkdir /opt/drill/log
sudo chmod 777 /opt/drill/log
sudo curl -s "http://download.nextag.com/apache/drill/drill-1.9.0/apache-drill-1.9.0.tar.gz" | sudo tar xz --strip=1 -C /opt/drill
sudo yum install -y java-1.8.0-openjdk
sudo yum install -y python35
sudo yum install -y aws-cli
sudo yum install -y unzip

# Get Files

git clone https://github.com/arturld/awsDBRDownload.git
cd awsDBRanalysis
./run.sh
