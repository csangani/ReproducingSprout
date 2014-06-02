## Run an experiment (d'oh)

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost

import os
import subprocess
import sys
import time

## Output directories
OUTPUT_PATH = '/home/cs244-sprout/experiment/results'

## Testbed directories
CELLSIM_PATH = '/home/cs244-sprout/experiment/multisend/sender/cellsim'
TRACES_PATH = '/home/cs244-sprout/experiment/cleaned_traces'

## Application directories
SPROUT_PATH = '/home/cs244-sprout/experiment/alfalfa/src/examples/sproutbt2'

class CellsimTopo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        client = self.addHost('client')
        cellsim = self.addHost('cellsim')
        server = self.addHost('server')
        
        self.addLink(client, cellsim, bw = 1000, delay = '1ms')
        self.addLink(cellsim, server, bw = 1000, delay = '1ms')

def run_cellsim(testbed, network, destination):
    cellsim = testbed.get('cellsim')
    client = testbed.get('client')
    
    # Run cellsim
    cellsim.popen('%s %s %s %s 0 %s %s > %s/cellsim.out 2>&1' % (
        CELLSIM_PATH,
        '%s/%s/uplink.pps' % (TRACES_PATH, network),
        '%s/%s/downlink.pps' % (TRACES_PATH, network),
        client.MAC(client.intfs[0].name),
        cellsim.intfs[1].name,
        cellsim.intfs[0].name,
        destination
    ), shell = True)

def setup_testbed(testbed):
    cellsim = testbed.get('cellsim')
    client = testbed.get('client')
    server = testbed.get('server')
    
    # Set cellsim interfaces to promiscuous mode
    cellsim.cmd('ifconfig %s up promisc' % cellsim.intfs[0].name)
    cellsim.cmd('ifconfig %s up promisc' % cellsim.intfs[1].name)
    
    # Turn off segmentation offloading on all interfaces
    for node in [cellsim, server, client]:
        for intf in node.intfs.values():
            node.cmd('ethtool --offload %s gso off tso off gro off' % intf.name)

def wait(delay, message):
    sys.stdout.write('\r**** %s (%.2f%%)' % (message, 0))
    sys.stdout.flush()
    for i in range(1,delay+1):
        time.sleep(1)
        sys.stdout.write('\r**** %s (%.2f%%)' % (message, i * 100. / delay))
        sys.stdout.flush()
    print
    
def run_experiment(network, application):
    destination = '%s/%s/%s' % (OUTPUT_PATH, network, application)
    
    if not os.path.exists(destination):
        os.makedirs(destination)
    
    topo = CellsimTopo()
    testbed = Mininet(topo = topo, host = CPULimitedHost, link = TCLink)
    testbed.start()
    
    try:
        client = testbed.get('client')
        server = testbed.get('server')
        
        print '**** Setting up testbed'
        setup_testbed(testbed)
        
        if application == 'sprout':
            
            # Run sproutbt2 server and client
            server.popen('%s' % SPROUT_PATH, shell = True)
            client.popen('%s %s 60001' % (SPROUT_PATH, server.IP()), shell = True)
            wait(60, 'Starting Sprout benchmark test')
            
            # Run cellsim
            run_cellsim(testbed, network, destination)

            wait(1020, 'Running experiment')
            
        elif application.split('_')[0] == 'tcp':
            
            # Set TCP type
            type = application.split('_')[1]
            
            # Install TCP module
            subprocess.Popen('modprobe tcp_%s' % type, shell = True)
            
            # Set TCP congestion control
            subprocess.Popen('echo "%s" > /proc/sys/net/ipv4/tcp_congestion_control' % type, shell = True)
            
            # Run cellsim
            run_cellsim(testbed, network, destination)
            
            # Run iperf server and client
            server.popen('iperf -s', shell = True)
            wait(1, 'Starting iperf')
            client.popen('iperf -c %s -d -t 1020' % server.IP())
            
            wait(1020, 'Running experiment')
            
    finally:
        testbed.stop()
        subprocess.call('killall sproutbt2', shell = True)
        subprocess.call('killall iperf', shell = True)
        subprocess.call('killall cellsim', shell = True)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: python run_experiment.py <network> <application>'
        sys.exit(0)
        
    network = sys.argv[1]
    application = sys.argv[2]
    
    run_experiment(network, application)
