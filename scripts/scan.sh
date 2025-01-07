#!/bin/bash
data=$(date)
echo $data >> /var/log/disk.log 2>&1
void=$(sudo parted /dev/vda unit MB print free | grep 'Free Space' | wc -l)
if (($void >= 2)); then 
/opt/disk.sh >> /var/log/disk.log 2>&1
fi
