#!/bin/bash

TRACES_PATH=cleaned_traces
RESULTS_PATH=results
ERRORS_NETWORKS=( att verizon4g )

networks=$(ls $TRACES_PATH)
apps=( sprout tcp_cubic tcp_vegas tcp_reno )

for network in ${networks[@]}
do
    for app in ${apps[@]}
    do
        echo "**** Running $app on $network"
        python run_experiment.py $network $app
        echo "**** Extracting performance metrics"
        python extract_metrics.py $network $app
        mv $RESULTS_PATH/$network/$app/uplink-throughput $RESULTS_PATH/$network/$app/uplink-throughput-reproduce
        mv $RESULTS_PATH/$network/$app/uplink-delay $RESULTS_PATH/$network/$app/uplink-delay-reproduce
        mv $RESULTS_PATH/$network/$app/downlink-throughput $RESULTS_PATH/$network/$app/downlink-throughput-reproduce
        mv $RESULTS_PATH/$network/$app/downlink-delay $RESULTS_PATH/$network/$app/downlink-delay-reproduce
    done
done

echo "**** Creating plots"
python create_plots.py

echo -e "**** Done reproducing plots. Now running each\n**** application 5 times for 17 minutes over AT&T\n**** and Verizon 4G traces to produe error plots"

for net in ${ERRORS_NETWORKS[@]}
do  
    for i in 1 2 3 4 5
    do
        for app in ${apps[@]}
        do
            echo "**** Running $app on $net, iteration $i"
            python run_experiment.py $net $app
            echo "**** Extracting performance metrics"
            python extract_metrics.py $net $app
            mv $RESULTS_PATH/$net/$app/uplink-throughput $RESULTS_PATH/$net/$app/uplink-throughput-$i
            mv $RESULTS_PATH/$net/$app/uplink-delay $RESULTS_PATH/$net/$app/uplink-delay-$i
            mv $RESULTS_PATH/$net/$app/downlink-throughput $RESULTS_PATH/$net/$app/downlink-throughput-$i
            mv $RESULTS_PATH/$net/$app/downlink-delay $RESULTS_PATH/$net/$app/downlink-delay-$i
        done
    done
    echo "**** Creating $net plot"
    python create_plots.py $net
done 
