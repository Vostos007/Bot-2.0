#!/bin/bash
apt install ifupdown -y
apt-get -y purge nplan netplan.io
systemctl disable systemd-networkd
systemctl enable networking
sed -i '$d' /etc/crontab 
reboot now
