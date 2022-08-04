#
# Copyright (c) 2019-2020 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Multi-threaded sample to run a RMNet & SSDMobilenet v2 that will
# detect only person, bike and vehicle (change the output parsing
# for more classes)
#
# Example usage:
# RMNet: python3.6 multi_inputs.py -n "RMNet" -l "data" -o "detection_out"
# -d 1024 -i 127.0.0.1 -p 9001 -c 1
# -f /var/repos/github/sample-videos/person-bicycle-car-detection.mp4
# SSDMobileNet: python3.6 multi_inputs.py -n "SSDMobileNet" -l "image_tensor"
# -o "DetectionOutput" -d 300 -i 127.0.0.1 -p 9001 -c 1
# -f /var/repos/github/sample-videos/person-bicycle-car-detection.mp4

from __future__ import print_function
from argparse import ArgumentParser, SUPPRESS
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from time import time, sleep
import numpy as np
import sys
import os
import cv2
import grpc
import threading
import logging as log
from tensorflow import make_tensor_proto, make_ndarray
from PIL import Image
from matplotlib import pyplot as plt

# global data (shared between threads & main)
CLASSES = ["None", "Pedestrian", "Vehicle", "Bike", "Other"]
COLORS = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
SRC_TYPE = ["Camera", "Video"]

exit_ok = False             # manage thread loop
CAM_WIDTH = 512            # camera width
CAM_HEIGHT = 512            # camera height
CAM_FPS = 30                # camera speed
CONFIDENCE_THRESHOLD = 0.75 # detection confidence

#####################################################################################

def build_argparser():
  parser = ArgumentParser(add_help=False)
  args = parser.add_argument_group('Options')
  args.add_argument('-h', '--help', action='help', default=SUPPRESS,
        help='Show this help message and exit.')
  args.add_argument('-n', '--network_name', required=True,
        type=str, help='Network name')
  args.add_argument('-l', '--input_layer', required=True,
        type=str, help='Input layer name')
  args.add_argument('-o', '--output_layer', required=True,
        type=str, help='Output layer name')
  args.add_argument('-d', '--frame_size', required=True,
        type=int, help='Input frame width and height that matches used model')
  args.add_argument('-c', '--num_cameras', help='Number of cameras to be used',
        required=False, type=int, default=1)
  args.add_argument('-f', '--file', help='Path to the video file',
        required=False, type=str)
  args.add_argument('-i', '--ip', help='ip address of the ovms', required=True)
  args.add_argument('-p', '--port', help='port of the ovms', required=True)

  return parser

# This is common for both the camera & video files
def thread_function(thr_id, network_name, input_layer, output_layer, input_dimension,
                    ip, port, disp_buf, src_type, src_name):

  if src_type == "Camera":
    # UVC camera init - camera threads always come first and we use it
    # to generate the camera indexes
    cam = cv2.VideoCapture(thr_id)
    if not (cam.isOpened()):
      log.error("Failed to open the UVC camera {}".format(thr_id))
      return

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    # not all UVC cameras honor below request
    cam.set(cv2.CAP_PROP_FPS, CAM_FPS)
    # If your camera sends other than MJPEG, change below
    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
  elif src_type == "Video":
    # Assumption: src_name will be valid
    cam = cv2.VideoCapture(src_name)

  # inference stats
  fps = 0                   # camera fps
  inf_fps = 0               # inference fps
  dropped_fps = 0           # dropped frame fps
  cam_start_time = time()

  # ovms connection
  channel = grpc.insecure_channel("{}:{}".format(ip, port))
  stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

  request = predict_pb2.PredictRequest()      
  # Note: Pls maintain the same name while launching ovms docker container
  request.model_spec.name = network_name

  global exit_ok
  while exit_ok == False:
    ret, frame = cam.read()

    if src_type == "Video":
      # restart the video file when it reaches the end
      if not ret:
        cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
      # normalize the video frame dimension to that of the camera
      else:
        # to maintain the frame inferencing parity with the cameras, lets sleep
        # here to maintain cam_fps speed
        sleep((1000 / CAM_FPS) / 1000)
        # enable below line to keep video file & camera output window dimensions the same
        # frame = cv2.resize(frame, (CAM_WIDTH, CAM_HEIGHT))

    fps = fps + 1
    if (time() - cam_start_time) * 1000 >= 1000:
      log.warning('{}{} fps: {}, Inf fps: {}, dropped fps: {}'
                  .format(src_type, thr_id, fps, inf_fps, dropped_fps))
      fps = 0
      inf_fps = 0
      dropped_fps = 0
      cam_start_time = time()

    # resize the frame to what network input layer expects it to be
    image = cv2.resize(frame, (input_dimension, input_dimension))
    image = image.transpose(2, 0, 1).reshape(1, 3, input_dimension, input_dimension)
    image = image.astype('float32')

    inf_time = time()
    # send the input as protobuf
    request.inputs[input_layer].CopyFrom(
        make_tensor_proto(image, shape=None))

    try:
      result = stub.Predict(request, 10.0)
    except Exception as e:
      log.error('Caught exception {}'.format(e))
      cam.release()
      return
    duration = time() - inf_time

    # decode the received output as protobuf
    res = make_ndarray(result.outputs[output_layer])
    print(res.dtype)
    resArr = np.resize(res, (352, 352))
    aMin = np.amin(resArr)
    aMax = np.amax(resArr)
    print( aMin, ',', aMax)
    #print(np.finfo(resArr.dtype).max)

    resArr = resArr.astype(np.float64) / (aMax - aMin)
    resArr = (1 + resArr) * 255
    #print(resArr)
    resArr[resArr < 100] = 0
    resArr = resArr.astype(np.uint8)
    final = np.invert(resArr)
    for i in range(352):
      for j in range(352):
        if final[i][j] < 150:
          final[i][j] = 0
        else:
          final[i][j] = 255
    if not res.any():
     log.error('Thr{}: Predictions came back with wrong output layer name'.format(thr_id))
     dropped_fps = dropped_fps + 1
     disp_buf[thr_id] = frame
    else:
     log.debug('Predictions came back fine')
     inf_fps = inf_fps + 1
     disp_buf[thr_id] = final
#parse_output(thr_id, resArr, frame)

  # while exit_ok == False

  cam.release()
  log.warning('Exiting thread {}'.format(thr_id))

#####################################################################################

def main():
  log.basicConfig(format="[$(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
  args = build_argparser().parse_args()
  num_cam = args.num_cameras if (args.num_cameras) else 0
  vid_src = args.file
  network_name = args.network_name
  input_layer = args.input_layer
  output_layer = args.output_layer
  input_dimension = args.frame_size
  ip_addr = args.ip
  port_no = args.port

  if not args.file and not args.num_cameras:
    log.error('Please supply either the camera or the video file. Try -f for options')
    return

  if not ip_addr or not port_no:
    log.error('Please supply valid IP and/or port number of OVMS server')
    return

  video_files = []
  if vid_src:
    if os.path.isdir(vid_src):
      for r, d, f in os.walk(vid_src):
        for f_ in f:
          # only mp4 files supported as of now
          if '.mp4' in f_:
            video_files.append(r + f_)
    elif os.path.isfile(vid_src):
      if '.mp4' in vid_src:
        video_files.append(vid_src)

  # thread management
  thr = [None] * (num_cam + len(video_files))
  # display buffers shared between camera threads
  disp_buf = {}

  # Known issue: Depending on the USB enumeration, camera nodes need not be
  # in sequence. Pls pass the device node info through a file or command line
  # if it happens in your system
  for i in range(num_cam):
    disp_buf[i] = None
    thr[i] = threading.Thread(target=thread_function,
                args=(i, network_name, input_layer, output_layer, input_dimension,
                ip_addr, port_no, disp_buf, SRC_TYPE[0], None))
    thr[i].start()

  for i in range(num_cam, num_cam + len(video_files)):
    disp_buf[i] = None
    thr[i] = threading.Thread(target=thread_function,
                args=(i, network_name, input_layer, output_layer, input_dimension,
                ip_addr, port_no, disp_buf, SRC_TYPE[1], video_files[i - num_cam]))
    thr[i].start()

  # For whatever reasons, cv2.imshow() doesnt work from threads. Hence we shove the
  # infered data to the main thread to display.
  global exit_ok
  while exit_ok == False:
    for i in range(num_cam + len(video_files)):
      if disp_buf[i] is not None:
        cv2.imshow('Dexi Stream', disp_buf[i])
        disp_buf[i] = None

      # exit the program if 'q' is pressed on any window
      if cv2.waitKey(1) == ord('q'):
        exit_ok = True
        break

  # wait for all the threads to join
  for i in range(num_cam):
    thr[i].join()

  # close all open windows
  cv2.destroyAllWindows()
  log.warning('Good Bye!')

if __name__ == '__main__':
  sys.exit(main() or 0)
