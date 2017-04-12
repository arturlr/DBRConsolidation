#!/bin/bash

# INSTALL PRE-REQS
sudo yum update -y
sudo chmod 777 /media/ephemeral0/
sudo mkdir /opt/drill
sudo mkdir /opt/drill/log
sudo chmod 777 /opt/drill/log
sudo yum install -y java-1.8.0-openjdk
sudo curl -s "http://download.nextag.com/apache/drill/drill-1.9.0/apache-drill-1.9.0.tar.gz" | sudo tar xz --strip=1 -C /opt/drill
sudo yum install -y python35
sudo yum install -y aws-cli
sudo yum install -y unzip
sudo yum install -y git

# Install and update pip
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user
~/.local/bin/pip install -U pip

# Prep Libraries
~/.local/bin/pip install boto3
~/.local/bin/pip install cloudwatch-fluent-metrics

# Get Files
cd ~
git clone https://github.com/arturlr/DBRConsolidation
cd DBRConsolidation
./run.sh
