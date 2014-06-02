## Creates oracular traces from network traces, used for calculating self-inflicted delay

import glob
import os
import re
import sys

INPUT_PATH = '/home/cs244-sprout/experiment/cleaned_traces'
OUTPUT_PATH = '/home/cs244-sprout/experiment/oracular_traces'

def create_oracular_trace(filePath, targetFilePath, mode):
    with open(filePath) as f:
        with open(targetFilePath, 'w+') as wf:
            firstLine = True
            for line in f:
                value = long(line)
                if firstLine:
                    base = value
                    firstLine = False
                value = (value - base) / 1000.
                wf.write('%s %s delivery 20\n' % (mode, value))
                
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
        
        files = glob.glob('%s/*.pps' % network)
    
        for file in files:
            mode = re.findall('(uplink|downlink)', file)[0]
            create_oracular_trace(file, file.replace(source, destination).replace('.pps', '.out'), mode)
