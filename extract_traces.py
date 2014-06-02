## Create a network trace from the saturator output

import glob
import os
import sys

INPUT_PATH = '/home/cs244-sprout/experiment/raw_traces'
OUTPUT_PATH = '/home/cs244-sprout/experiment/cleaned_traces'

def extract_trace(filePath, targetFilePath):
    with open(filePath) as f:
        with open(targetFilePath, 'w+') as wf:
            firstLine = True
            for line in f:
                value = long(line.lstrip('recv_time=').rstrip(',\n'))
                if firstLine:
                    base = value
                    firstLine = False
                value = (value - base) / 1000000
                wf.write('%s\n' % value)
                
if __name__ == '__main__':
    if len(sys.argv) >= 2:
        source = sys.argv[1]
    else:
        source = INPUT_PATH
        
    if len(sys.argv) >= 3:
        destination = sys.argv[2]
    else:
        destination = OUTPUT_PATH
        
    if not os.path.exists(destination):
        os.makedirs(destination)
    
    networks = glob.glob('%s/*' % source)
    
    for network in networks:
        
        if not os.path.exists(network.replace(source, destination)):
            os.makedirs(network.replace(source, destination))
        
        files = glob.glob('%s/*.rx' % network)
    
        for file in files:
            extract_trace(file, file.replace(source, destination).replace('.rx', '.pps'))
