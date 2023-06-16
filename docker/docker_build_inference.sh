#!/usr/bin/env bash
sudo docker build --network=host -t kevywilly/nano-ml-inference:1.0 --build-arg CACHEBUST=$(date +%s) -f DockerInference .
