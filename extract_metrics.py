## Extract throughput / delay values from application traces

import os
import re
import subprocess
import sys

RESULTS_PATH = '/home/cs244-sprout/experiment/results'
TRACES_PATH = '/home/cs244-sprout/experiment/cleaned_traces'
ORACULAR_TRACES_PATH = '/home/cs244-sprout/experiment/oracular_traces'

SCORER_PATH = '/home/cs244-sprout/experiment/alfalfa/src/examples/scorer'
QUANTILES_PATH = '/home/cs244-sprout/experiment/alfalfa/src/examples/quantiles'

def extract_metrics(trace_file, mode):
    subprocess.call('cat %s | %s %s > temp1 2> temp2' % (trace_file, SCORER_PATH, mode), shell = True)
    subprocess.call('cat temp1 | %s >> temp2 2>&1' % QUANTILES_PATH, shell = True)
    
    with open('temp2') as f:
        data = f.read();

    os.remove('temp1')
    os.remove('temp2')
    
    throughput_metrics = re.findall('Used (\d+) kbps / (\d+) kbps => ([\d.]+) %', data)
    
    if len(throughput_metrics) > 0:
        throughput, capacity, utilization = throughput_metrics[0]
    else:
        throughput, capacity, utilization = (0, 0, 0)
    
    delay_metrics = re.findall('med: (\d+), 95th: (\d+)', data)
    
    if len(delay_metrics) > 0:
        median_delay, ninety5_delay = delay_metrics[0]
    else:
        median_delay, ninety5_delay = (0, 0)
    
    return int(throughput), int(ninety5_delay)
    
def run(network, application):
    assert(os.path.exists(SCORER_PATH))
    assert(os.path.exists(QUANTILES_PATH))

    input_file = '%s/%s/%s/cellsim.out' % (RESULTS_PATH, network, application)
    oracular_trace_files = [
        '%s/%s/uplink.out' % (ORACULAR_TRACES_PATH, network),
        '%s/%s/downlink.out' % (ORACULAR_TRACES_PATH, network)
    ]
    
    uplink_throughput, uplink_delay = extract_metrics(input_file, 'uplink')
    _, uplink_oracular_delay = extract_metrics(oracular_trace_files[0], 'uplink')
    
    downlink_throughput, downlink_delay = extract_metrics(input_file, 'downlink')
    _, downlink_oracular_delay = extract_metrics(oracular_trace_files[1], 'downlink')
    
    with open('%s/%s/%s/uplink-throughput' % (RESULTS_PATH, network, application), 'w+') as f:
        f.write(str(uplink_throughput))
        
    with open('%s/%s/%s/uplink-delay' % (RESULTS_PATH, network, application), 'w+') as f:
        f.write(str(uplink_delay - uplink_oracular_delay))
        
    with open('%s/%s/%s/downlink-throughput' % (RESULTS_PATH, network, application), 'w+') as f:
        f.write(str(downlink_throughput))
        
    with open('%s/%s/%s/downlink-delay' % (RESULTS_PATH, network, application), 'w+') as f:
        f.write(str(downlink_delay - downlink_oracular_delay))
    
if __name__ == '__main__':
    assert(len(sys.argv) == 3)
        
    network = sys.argv[1]
    application = sys.argv[2]
    
    run(network, application)
