import argparse

def parse_args():
    modes_choices = ['CreateDataset', 'Run', 'AnalyzeDataset', 'Train', 'LabelVideo', 'LiveTrain', 'LiveRec']
    parser = argparse.ArgumentParser(description='AI Race main control')
    parser.add_argument('mode', type=str, help='Mode in which to run the application', choices=modes_choices, default='Run')
    parser.add_argument('-i', '--input_file', type=str, help='Input file', default='')
    parser.add_argument('-r', '--render', type=bool, help='Render feed', default=False)
    parser.add_argument('-d', '--dataset_location', type=str, help='Dataset folder to analyze', default=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    print(args)
