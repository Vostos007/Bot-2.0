#!/bin/bash
void=$(sudo parted /dev/vda unit MB print free | grep 'Free Space' | wc -l)
echo $(date) $void >> /var/log/disk.log
(
echo d # del a partition
echo 1
echo n # Add a new partition
echo p # Partition number
echo 1
echo   # First sector (Accept default: 1)
echo   # Last sector (Accept default: varies)
#echo n 
echo w # Write changes
) | sudo fdisk /dev/vda
sudo partprobe /dev/vda
sudo resize2fs /dev/vda1
