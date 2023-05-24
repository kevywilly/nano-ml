#!/usr/bin/env bash
echo "Stopping nanoml.service..."
sudo systemctl nanoml stop
echo "nanoml.service stopped."
echo "starting docker"
./docker_runner.sh  -c kevywilly/nano-ml:1.0 -v /home/nano:/nano -r /nano_ml/start_trainer.sh
