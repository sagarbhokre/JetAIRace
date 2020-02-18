#!/usr/bin/python3

# reference: https://github.com/JetsonHacksNano/CSI-Camera

import cv2
import os
import uuid
import copy
import subprocess
from jetcam.csi_camera import CSICamera

class JCamera:
    def __init__(self, handle_keys = True, render = True):
        self.refPt = [(0,0)]
        self.dataset_dir = os.getcwd() + '/dataset'
        self.handle_keys = handle_keys
        self.width = 224
        self.height = 224
        self.render = render
        self.init_gcamera()

    def gstreamer_pipeline(
        self,
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=60,
        flip_method=0,
    ):
        return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
        )

    def init_gcamera(self):
        self.camera = cv2.VideoCapture(self.gstreamer_pipeline(flip_method=0, display_width = self.width, display_height = self.height), cv2.CAP_GSTREAMER)
        if self.camera.isOpened():
            print("Open camera success!")
        else:
            print("Failed to open camera")
            return

        cv2.namedWindow("CSI Camera feed")
        cv2.setMouseCallback("CSI Camera feed", self.click_and_save)

    def start(self):

        while True:
            ret, self.image = self.camera.read()
            if self.render:
                h,w,c = self.image.shape
                self.image = cv2.line(self.image, (0,int(h/2)), (w,int(h/2)), (0,255,0), 1)
                cv2.imshow("CSI Camera feed", self.image)

            if self.handle_keys:
                k = cv2.waitKey(33) & 0xFF
                if k == 27 or k == ord('q'):
                    break
            else:
                return
           
    def click_and_save(self, event, x, y, flags, param):
        # grab references to the global variables
        if event == cv2.EVENT_LBUTTONDOWN:
            self.refPt = [(x, y)]
            self.x = x
            self.y = y
            print(x,y)
            self.image_overlay = copy.copy(self.image)
            self.image_overlay = cv2.circle(self.image_overlay, (x, y), 8, (0, 255, 0), 3)
            cv2.imshow("CSI Camera feed", self.image_overlay)
            self.save_entry()

    def getFrame(self):
        ret, self.image = self.camera.read()
        if self.render:
            h,w,c = self.image.shape
            self.image_overlay = copy.copy(self.image)
            self.image_overlay = cv2.line(self.image_overlay, (0,int(h/2)), (w,int(h/2)),
                                          (0,255,0), 1)
            cv2.imshow("CSI Camera feed", self.image_overlay)
        return ret, self.image

    def read(self):
        return self.getFrame()

    def stop(self):
        self.camera.release()
        cv2.destroyAllWindows()

    def release(self):
        return self.stop()

    def save_entry(self):
        if not os.path.exists(self.dataset_dir):
            subprocess.call(['mkdir', '-p', self.dataset_dir])
    
        filename = '%d_%d_%s.jpg' % (self.x, self.y, str(uuid.uuid1()))
    
        image_path = os.path.join(self.dataset_dir, filename)
        cv2.imwrite(image_path, self.image)

if __name__ == '__main__':
    cam = JCamera(handle_keys=True)
    cam.start()
    cam.stop()
