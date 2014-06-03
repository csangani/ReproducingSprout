num_runs=5
#for network in "att" "verizon3g" "verizon4g" "sprint" "tmobile"; do
#for network in "verizon3g" "verizon4g" "sprint" "tmobile"; do
for network in "tmobile"; do
  for application in "sprout" "tcp_vegas" "tcp_cubic" "tcp_reno"; do 
    for i in $(seq 1 $num_runs); do 
      echo "$network $application run: $i"
      sudo python run_experiment.py $network $application
      sudo python extract_metrics.py $network $application
    done
  done
done
