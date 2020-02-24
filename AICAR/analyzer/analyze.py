import os
import cv2
import glob
import copy
import uuid
from .utils import *

default_dataset_dir = os.getcwd()+'/../road_following_A/apex/'

refPt = [0,0]
def click_and_save(event, x, y, flags, param):
    global refPt, dataset_dir, image_overlay
    # grab references to the global variables
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        x = x
        y = y
        print(x,y)
        image_overlay = cv2.circle(image_overlay, (x, y), 8, (255, 0, 0), 3)
        save_entry(x, y)

def save_entry(x, y):
    global fname, img
    if not os.path.exists(dataset_dir):
        subprocess.call(['mkdir', '-p', dataset_dir])

    filename = '%d_%d_%s.jpg' % (x, y, str(uuid.uuid1()))

    image_path = os.path.join(dataset_dir, filename)
    cv2.imwrite(image_path, img)
    print('rm %s'%(fname))
    os.system('rm %s'%(fname))
    print('create %s'%(image_path))

img = None
image_overlay = None
def render_file(fname):
    global img, image_overlay
    (x,y) = [int(x) for x in fname.strip().split('/')[-1].split('_')[0:2]]
    img = cv2.imread(fname)
    h,w,c = img.shape
    image_overlay = copy.copy(img)
    image_overlay = cv2.circle(image_overlay, (x, y), 8, (0, 255, 0), 3)
    image_overlay = cv2.line(image_overlay, (0,int(h*2/3)), (w,int(h*2/3)),
                                          (0,255,0), 1)
    image_overlay = cv2.line(image_overlay, (int(w/2),0), (int(w/2),h), (0,255,0), 1)
    cv2.imshow("Analyze dataset", image_overlay)

dataset_dir = ''
fname = ''
def analyze_dataset(dataset_dir_in):
    cv2.namedWindow("Analyze dataset")
    cv2.setMouseCallback("Analyze dataset", click_and_save)
    global dataset_dir, fname
    dataset_dir = dataset_dir_in
    flist = get_files_list(dataset_dir)
    count = 0
    while count < len(flist) and count >= 0:
        f = flist[count]
        if(not os.path.exists(f)):
            count += 1
            continue
        fname = f
        print(f)
        render_file(f)
        k = cv2.waitKey(0) & 0xFF
        if(k == 27):
            exit(1)
        elif k == 83:
            count += 1
        elif k == 81:
            count -= 1
        elif(k == ord('d')):
            os.system('rm %s'%(fname))
            print('rm %s'%(fname))
            count += 1

if __name__ == '__main__':
    flist = get_files_list(default_dataset_dir)
    count = 0
    while count < len(flist) and count >= 0:
        f = flist[count]
        print(f)
        render_file(f)
        k = cv2.waitKey(0) & 0xFF
        if(k == 27):
            exit(1)
        elif k == 83:
            count += 1
        elif k == 81:
            count -= 1
        elif(k == ord('d')):
            os.system('rm %s'%(fname))
            print('rm %s'%(fname))
