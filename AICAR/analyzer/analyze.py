import os
import cv2

default_dataset_dir = os.getcwd()+'/../dataset/'

def get_files_list(dataset_dir):
    files = []
    for r,d,f in os.walk(dataset_dir):
        for fname in f:
            if '.jpg' in fname:
                files.append(os.path.abspath(os.path.join(r, fname)))
    if len(files) == 0:
        print("Could not locate files in dataset dir: %s"%(dataset_dir))
    return files


def render_file(fname):
    (x,y) = [int(x) for x in fname.strip().split('/')[-1].split('_')[0:2]]
    img = cv2.imread(fname)
    img = cv2.circle(img, (x, y), 8, (0, 255, 0), 3)
    cv2.imshow("Analyze dataset", img)
    k = cv2.waitKey(0) & 0xFF
    if(k == 27):
        exit(1)
    elif k == 83:
        return

def analyze_dataset(dataset_dir):
    flist = get_files_list(dataset_dir)
    for f in flist:
        render_file(f)
        print(f)

if __name__ == '__main__':
    flist = get_files_list(default_dataset_dir)
    for f in flist:
        render_file(f)
        print(f)
