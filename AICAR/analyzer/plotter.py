import os
import glob
import sys
from utils import *
from matplotlib import pyplot as plt

def get_distribution(flist):
    steerings = []

    for fname in flist:
        vals = fname.split('/')[-1]
        print(vals)
        vals = vals.split('_')
        print(vals)
        steerings.append(int(vals[0]))

    return steerings

def plot_distribution(data):
    #plt.plot(data)
    plt.hist(data, normed=True, bins=30)
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 plotter.py <folder>")
        exit(1)

    flist = get_files_list(sys.argv[1])
    data = get_distribution(flist)
    plot_distribution(data)
    print(len(flist))

