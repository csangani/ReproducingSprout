## Create a network trace using specified distribution for packet intervals

import math
import numpy
import os
import random
import sys

UPLINK_TRACE_SIZE = 30000
DOWNLINK_TRACE_SIZE = 350000

TRACES_PATH = '/home/cs244-sprout/experiment/cleaned_traces'

def create_trace(d_name, d_function, mode):
    intervals = [int(round(abs(d_function()))) for _ in range(UPLINK_TRACE_SIZE if mode == 'uplink' else DOWNLINK_TRACE_SIZE)]
    values = []
    current_value = 0
    for i in intervals:
        values += [current_value]
        current_value += i
        
    with open('%s/%s/%s.pps' % (TRACES_PATH, d_name, mode), 'w+') as f:
        for v in values:
            f.write('%s\n' % v)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python create_trace.py <distribution>'
        sys.exit(1)
        
    d_name = sys.argv[1]
    
    if not os.path.exists('%s/%s' % (TRACES_PATH, d_name)):
        os.makedirs('%s/%s' % (TRACES_PATH, d_name))
    
    if d_name == 'gauss':
        uplink_function = lambda: random.gauss(14.383, 298.962)
        downlink_function = lambda: random.gauss(2.320, 11.526)
        
    elif d_name == 'expovariate':
        uplink_function = lambda: random.expovariate(1 / 14.383)
        downlink_function = lambda: random.expovariate(1 / 2.320)
        
    elif d_name == 'poisson':
        uplink_function = lambda: numpy.random.poisson(14.383)
        downlink_function = lambda: numpy.random.poisson(2.320)
        
    elif d_name == 'uniform':
        uplink_function = lambda: random.uniform(0,30)
        downlink_function = lambda: random.uniform(0,10)
    
    else:
        print "Unrecognized distribution"
        sys.exit(1)
    
    create_trace(d_name, uplink_function, 'uplink')
    create_trace(d_name, downlink_function, 'downlink')
