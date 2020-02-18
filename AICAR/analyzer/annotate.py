import cv2
import os
import copy
import uuid

class JLabeler:
    def __init__(self):
        self.cap = None
        self.dataset_dir = os.getcwd()+'/../road_following_A/apex/'
        cv2.namedWindow("Video feed")
        cv2.setMouseCallback("Video feed", self.click_and_save)


    def save_entry(self):
        if not os.path.exists(self.dataset_dir):
            subprocess.call(['mkdir', '-p', self.dataset_dir])

        filename = '%d_%d_%s.jpg' % (self.x, self.y, str(uuid.uuid1()))

        image_path = os.path.join(self.dataset_dir, filename)
        cv2.imwrite(image_path, self.image)

    def click_and_save(self, event, x, y, flags, param):
        # grab references to the global variables
        if event == cv2.EVENT_LBUTTONDOWN:
            self.refPt = [(x, y)]
            self.x = x
            self.y = y
            print(x,y)
            self.image_overlay = cv2.circle(self.image_overlay, (x, y), 8, (0, 255, 0), 3)
            cv2.imshow("Video feed", self.image_overlay)
            self.save_entry()

    def label_video(self, fname):
        self.cap = cv2.VideoCapture(fname)
        while True:
            ret, self.image = self.cap.read()
            if ret == False:
                break

            self.image_overlay = copy.copy(self.image)
            h,w,c = self.image.shape
            self.image_overlay = cv2.line(self.image_overlay, (0,int(h/2)), (w,int(h/2)),
                                          (0,255,0), 1)
            cv2.imshow("Video feed", self.image_overlay)
            k = cv2.waitKey(0) & 0xFF
            if k == ord('n'):
                continue
            elif k == ord('q') or k == 27:
                break
