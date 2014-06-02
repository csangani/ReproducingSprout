#!/bin/bash

TRACES_PATH=cleaned_traces
RESULTS_PATH=results
ERRORS_NETWORK=att

networks=$(ls $TRACES_PATH)
apps=( sprout tcp_cubic tcp_vegas tcp_reno )

for i in 1 2 3 4 5
do
    for app in ${apps[@]}
    do
        echo "**** Running $app on $ERRORS_NETWORK, iteration $i"
        python run_experiment.py $ERRORS_NETWORK $app
        echo "**** Extracting performance metrics"
        python extract_metrics.py $ERRORS_NETWORK $app
        mv $RESULTS_PATH/$ERRORS_NETWORK/$app/uplink-throughput $RESULTS_PATH/$ERRORS_NETWORK/$app/uplink-throughput-$i
        mv $RESULTS_PATH/$ERRORS_NETWORK/$app/uplink-delay $RESULTS_PATH/$ERRORS_NETWORK/$app/uplink-delay-$i
        mv $RESULTS_PATH/$ERRORS_NETWORK/$app/downlink-throughput $RESULTS_PATH/$ERRORS_NETWORK/$app/downlink-throughput-$i
        mv $RESULTS_PATH/$ERRORS_NETWORK/$app/downlink-delay $RESULTS_PATH/$ERRORS_NETWORK/$app/downlink-delay-$i
    done
done

for network in ${networks[@]}
do
    for app in ${apps[@]}
    do
        echo "**** Running $app on $network"
        python run_experiment.py $network $app
        echo "**** Extracting performance metrics"
        python extract_metrics.py $network $app
    done
done

echo "**** Creating plots"
python create_plots.py att
