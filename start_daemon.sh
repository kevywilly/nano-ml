#!/bin/bash
sudo docker run -it --runtime nvidia  \
--network host \
--rm \
--device /dev/video0 --device /dev/i2c-0  --device /dev/i2c-1  \
-v /tmp/argus_socket:/tmp/argus_socket -v /ml_data:/ml_data  -v /home/nano:/nano  \
kevywilly/nano-ml:1.0
# -rm -d --restart unless-stopped