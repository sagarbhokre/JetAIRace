import argparse

def parse_args():
    modes_choices = ['CreateDataset', 'Run', 'AnalyzeDataset']
    parser = argparse.ArgumentParser(description='AI Race main control')
    parser.add_argument('mode', type=str, help='Mode in which to run the application', choices=modes_choices, default='Run')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    print(args)
