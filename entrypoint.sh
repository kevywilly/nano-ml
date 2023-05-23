#!/bin/bash
/etc/init.d/nginx start
cd /nano_ml && ./api.py
