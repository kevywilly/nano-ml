#!/usr/bin/python3
from jetson_utils import videoSource, videoOutput, Log

input = videoSource("csi://0", argv=['--input-flip=rotate-180'])

#input = videoSource("csi://0")
numFrames=0

while True:
    # capture the next image
    img = input.Capture()
    
    if img is None:
        continue

    if numFrames % 25 == 0 or numFrames < 15:
        Log.Verbose(f"video-viewer:  captured {numFrames} frames ({img.width} x {img.height})")

    numFrames +=1

    if not input.IsStreaming():
        break
