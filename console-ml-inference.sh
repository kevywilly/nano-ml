#!/bin/bash
cd ~/jetson-inference && docker/run.sh --volume /home/nano:/nano --container kevywilly/nano-ml-inference:1.0 -r /bin/bash

