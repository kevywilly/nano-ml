
## Useful Links

https://maker.pro/nvidia-jetson/tutorial/how-to-use-gpio-pins-on-jetson-nano-developer-kit

https://alexsm.com/flask-serve-images-on-the-fly/

https://developer.nvidia.com/blog/accelerating-inference-up-to-6x-faster-in-pytorch-with-torch-tensorrt/

## Inference Build Settings

```
# must disable NVMM
cd jetson-inference/build
cmake -DENABLE_NVMM=off ../
make -j$(nproc)
sudo make install
```
