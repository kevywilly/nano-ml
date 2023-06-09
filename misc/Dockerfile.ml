FROM nvcr.io/nvidia/l4t-ml:r32.7.1-py3

RUN git clone https://github.com/NVIDIA-AI-IOT/jetcam
RUN cd jetcam && python3 setup.py install
RUN cd ../
RUN rm -rf jetcam

RUN git clone https://github.com/NVIDIA-AI-IOT/torch2trt
RUN cd torch2trt && python3 setup.py install
RUN cd ../
RUN rm -rf torch2trt

RUN pip3 install --no-cache-dir --verbose Adafruit_MotorHAT Adafruit_SSD1306 sparkfun-qwiic flask flask-cors

RUN apt-get update && apt-get install -y --no-install-recommends \
  && apt-get install -y unzip vim nginx \
  && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/sites-available/default

RUN git clone https://github.com/kevywilly/nano-control
RUN cp -r nano-control/build /var/www/build
RUN rm -rf nano-control