
## Useful Links

https://maker.pro/nvidia-jetson/tutorial/how-to-use-gpio-pins-on-jetson-nano-developer-kit

## Inference Build Settings

'''
# must disable NVMM
cd jetson-inference/build
cmake -DENABLE_NVMM=off ../
make
sudo make install
'''
