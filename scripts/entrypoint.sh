#!/bin/bash
/etc/init.d/nginx start
echo 38 > /sys/class/gpio/export || true
echo 200 > /sys/class/gpio/export || true
echo out > /sys/class/gpio/gpio200/direction
echo 1 > /sys/class/gpio/gpio200/value
echo out > /sys/class/gpio/gpio38/direction
echo 1 > /sys/class/gpio/gpio38/value
cd /nano_ml && ./api.py
