#!/bin/bash
echo "updating nano-control"
git submodule update --recursive --remote
echo "deploying nano-control"
sudo rm -rf /var/www/build && sudo cp -r nano-control/build /var/www/build
echo "restarting nginx"
sudo systemctl restart nginx
echo "done."
