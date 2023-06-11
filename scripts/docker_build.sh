#!/usr/bin/env bash
sudo docker build --network=host -t kevywilly/nano-ml:1.0 --build-arg CACHEBUST=$(date +%s) -f docker/Dockerfile .
