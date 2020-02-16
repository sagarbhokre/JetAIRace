#!/usr/bin/python3

from parser.util import *
from analyzer.analyze import *
from manual_control.car import JCar
from capture_utils.gcapture import JCamera

if __name__ == '__main__':
    args = parse_args()
    if args.mode == 'CreateDataset':
        cam = JCamera(handle_keys=False)
        car = JCar()

        ret = True
        while ret:
            ret, frame = cam.getFrame()
            ret = car.handle_keys()

    elif args.mode == 'Run':
        print("Currently unsupported mode")
        #run_car()
        exit(1)

    elif args.mode == 'AnalyzeDataset':
        analyze_dataset("./dataset")
