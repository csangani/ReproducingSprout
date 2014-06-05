## Create plots (d'oh)

import matplotlib.pyplot as plt
import numpy

import os
import sys

NUM_ITERATIONS = 5

TRACES_PATH = 'cleaned_traces'
PLOTS_PATH = 'plots'
RESULTS_PATH = 'results'

NETWORK_NAME = {
    'att': 'AT&T LTE',
    'sprint': 'Sprint',
    'verizon3g': 'Verizon 3G (1xEV-DO)',
    'verizon4g': 'Verizon LTE',
    'tmobile': 'T-Mobile 3G (UMTS)',
    'gauss': 'Gaussian Hypothetical',
    'poisson': 'Poisson Hypothetical',
    'expovariate': 'Exponential Hypothetical',
    'uniform': 'Uniform Hypothetical'
}

APPLICATION_NAME = {
    'sprout': 'Sprout',
    'tcp_cubic': 'TCP Cubic',
    'tcp_reno': 'TCP Reno',
    'tcp_vegas': 'TCP Vegas'
}

MARKER_STYLE = {
    'sprout': '*',
    'tcp_cubic': '+',
    'tcp_vegas': 'x',
    'tcp_reno': 'o'
}

COLOR = {
    'sprout': 'b',
    'tcp_cubic': 'r',
    'tcp_vegas': 'g',
    'tcp_reno': '#FFA500'
}

def read_data(path):
    with open(path) as f:
        return int(f.read())
    
def create_histogram(network):
    _histogram(network, 'uplink')
    _histogram(network, 'downlink')

def create_error_plot(network):
    apps = os.listdir('%s/%s' % (RESULTS_PATH, network))
    
    data = {}
    
    for app in apps:
        for i in range(1,NUM_ITERATIONS+1):
            try:
                uplink_throughput = read_data('%s/%s/%s/uplink-throughput-%s' % (RESULTS_PATH, network, app, i))
                uplink_delay = read_data('%s/%s/%s/uplink-delay-%s' % (RESULTS_PATH, network, app, i))
                downlink_throughput = read_data('%s/%s/%s/downlink-throughput-%s' % (RESULTS_PATH, network, app, i))
                downlink_delay = read_data('%s/%s/%s/downlink-delay-%s' % (RESULTS_PATH, network, app, i))

                if app not in data:
                    data[app] = {}

                data[app].update({
                    'ut-%s' % i: uplink_throughput,
                    'ud-%s' % i: uplink_delay,
                    'dt-%s' % i: downlink_throughput,
                    'dd-%s' % i: downlink_delay
                })

            except: pass
    
    for app in apps:
        data[app]['ut-mean'] = numpy.mean([data[app]['ut-%s' % i] for i in range(1,NUM_ITERATIONS+1)])
        data[app]['ut-std'] = numpy.std([data[app]['ut-%s' % i] for i in range(1,NUM_ITERATIONS+1)])
        
        data[app]['ud-mean'] = numpy.mean([data[app]['ud-%s' % i] for i in range(1,NUM_ITERATIONS+1)])
        data[app]['ud-std'] = numpy.std([data[app]['ud-%s' % i] for i in range(1,NUM_ITERATIONS+1)])
        
        data[app]['dt-mean'] = numpy.mean([data[app]['dt-%s' % i] for i in range(1,NUM_ITERATIONS+1)])
        data[app]['dt-std'] = numpy.std([data[app]['dt-%s' % i] for i in range(1,NUM_ITERATIONS+1)])
        
        data[app]['dd-mean'] = numpy.mean([data[app]['dd-%s' % i] for i in range(1,NUM_ITERATIONS+1)])
        data[app]['dd-std'] = numpy.std([data[app]['dd-%s' % i] for i in range(1,NUM_ITERATIONS+1)])
    
    _plot(network, data, 'uplink', error = True)
    _plot(network, data, 'downlink', error = True)

def create_plot(network):
    apps = os.listdir('%s/%s' % (RESULTS_PATH, network))
    
    data = {}
    
    for app in apps:
        try:
            uplink_throughput = read_data('%s/%s/%s/uplink-throughput-reproduce' % (RESULTS_PATH, network, app))
            uplink_delay = read_data('%s/%s/%s/uplink-delay-reproduce' % (RESULTS_PATH, network, app))
            downlink_throughput = read_data('%s/%s/%s/downlink-throughput-reproduce' % (RESULTS_PATH, network, app))
            downlink_delay = read_data('%s/%s/%s/downlink-delay-reproduce' % (RESULTS_PATH, network, app))

            data[app] = {
                'ut': uplink_throughput,
                'ud': uplink_delay,
                'dt': downlink_throughput,
                'dd': downlink_delay
            }
            
        except: pass
        
    _plot(network, data, 'uplink')
    _plot(network, data, 'downlink')
       
def _histogram(network, mode):
    with open('%s/%s/%s.pps' % (TRACES_PATH, network, mode)) as f:
        data = [int(l) for l in f.readlines()]
        
    intervals = []
    for i in range(1, len(data)):
        intervals += [data[i] - data[i-1]]
        
    fig = plt.figure()
    
    plt.hist(intervals, range = (0,100), bins = 40)
    
    plt.xlabel('Packet arrival interval (ms)')
    plt.ylabel('Frequency')
    
    plt.title('%s %s' % (NETWORK_NAME[network], mode.title()))
    
    fig.savefig('%s/histogram-%s-%s.png' % (PLOTS_PATH, network, mode))
    
    plt.close()
        
def _plot(network, data, mode, error = False):
    fig = plt.figure()

    ax = plt.subplot(111)
    ax.set_xscale('log')
    ax.invert_xaxis()

    plt.xlabel('Self-inflicted delay (ms)')
    plt.ylabel('Throughput (kbps)')
    
    plt.title('%s %s' % (NETWORK_NAME[network], mode.title()))

    if not error:
        for app in data:
            plt.scatter(
                data[app]['ud' if mode == 'uplink' else 'dd'],
                data[app]['ut' if mode == 'uplink' else 'dt'],
                marker = MARKER_STYLE[app],
                color = COLOR[app],
                label = APPLICATION_NAME[app],
                s = 60
            )
    
    else:
        for app in data:
            plt.scatter(
                data[app]['ud-mean' if mode == 'uplink' else 'dd-mean'],
                data[app]['ut-mean' if mode == 'uplink' else 'dt-mean'],
                marker = MARKER_STYLE[app],
                color = COLOR[app],
                label = APPLICATION_NAME[app],
                s = 60
            )
            plt.errorbar(
                data[app]['ud-mean' if mode == 'uplink' else 'dd-mean'],
                data[app]['ut-mean' if mode == 'uplink' else 'dt-mean'],
                data[app]['ud-std' if mode == 'uplink' else 'dd-std'],
                data[app]['ut-std' if mode == 'uplink' else 'dt-std'],
                fmt = None,
                color = COLOR[app]
            )
    for app in data:
        if not error:
            plt.annotate(APPLICATION_NAME[app],
                (data[app]['ud' if mode == 'uplink' else 'dd'],
                    data[app]['ut' if mode == 'uplink' else 'dt']),
                xytext=(10, -5), textcoords='offset points',)
        else:
            plt.annotate(APPLICATION_NAME[app],
                (data[app]['ud-mean' if mode == 'uplink' else 'dd-mean'],
                    data[app]['ut-mean' if mode == 'uplink' else 'dt-mean']),
                xytext=(10, 5), textcoords='offset points',)
                
    #plt.legend(scatterpoints = 1)

    if not error:
        fig.savefig('%s/%s-%s.png' % (PLOTS_PATH, network, mode))
    else:
        fig.savefig('%s/error-%s-%s.png' % (PLOTS_PATH, network, mode))
    
    plt.close()
    
if __name__ == '__main__':
    
    networks = os.listdir(RESULTS_PATH)

    if not os.path.exists(PLOTS_PATH):
        os.makedirs(PLOTS_PATH)
    if len(sys.argv) == 2:
        create_error_plot(sys.argv[1])    
    else:
    	for network in networks:
            create_plot(network)
            create_histogram(network)    
