import cv2
import copy

class JTouchSensor:
    def __init__(self, enable_prints=False, enable_render=False):
        self.enable_prints = enable_prints
        self.img = cv2.imread('/home/jetson/JetAIRace/AICAR/manual_control/Touch_BG.png')
        if enable_render:
            cv2.namedWindow("Touch Controller")
            cv2.setMouseCallback("Touch Controller", self.click_and_save)
            cv2.setWindowProperty("Touch Controller", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            self.img = cv2.resize(self.img, (1080, 340))
            self.h,self.w,self.c = self.img.shape
            cv2.moveWindow("Touch Controller", 0, -10);
            cv2.imshow("Touch Controller", self.img)
        self.xc = 0
        self.yc = 0

    def click_and_save(self, event, x, y, flags, param):
        # grab references to the global variables
        if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_MOUSEMOVE:
            refPt = [(x, y)]
            self.xc = 2.0 * (x * 1.0/self.w - 0.5)
            self.yc = 2.0 * (y * 1.0/self.h - 0.5)
            self.xc = self.xc if self.xc < 1.0 else 1.0
            self.xc = self.xc if self.xc > -1.0 else -1.0
            self.yc = self.yc if self.yc < 1.0 else 1.0
            self.yc = self.yc if self.yc > -1.0 else -1.0
            self.yc = self.yc * -1.0
            if self.enable_prints: print(self.xc, self.yc)
            #car.control(xc, 0)

if __name__ == '__main__':
    touch = JTouchSensor()
    while True:
        k = cv2.waitKey(100) & 0xFF
        if k == 27 or k == ord('q'):
            exit(1)
