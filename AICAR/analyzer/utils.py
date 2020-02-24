import glob
import os

def get_files_list(dataset_dir):
    files = []
    '''
    for r,d,f in os.walk(dataset_dir):
        for fname in f:
            if '.jpg' in fname:
                files.append(os.path.abspath(os.path.join(r, fname)))
    '''

    files = glob.glob(dataset_dir+"*.jpg")
    if len(files) == 0:
        print("Could not locate files in dataset dir: %s"%(dataset_dir))
    files.sort(key=os.path.getmtime)
    return files


