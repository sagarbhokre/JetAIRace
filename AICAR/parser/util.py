import argparse

def parse_args():
    modes_choices = ['CreateDataset', 'Run', 'AnalyzeDataset', 'Train', 'LabelVideo']
    parser = argparse.ArgumentParser(description='AI Race main control')
    parser.add_argument('mode', type=str, help='Mode in which to run the application', choices=modes_choices, default='Run')
    parser.add_argument('-i', '--input_file', type=str, help='Input file', default='')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    print(args)
