#!/bin/bash
#
# Perform a quick benchmark on all the nodes on GPU queue
# UNCOMMENT THIS WHILE DEBUGGING: set -x

PREFIX="gpu"
START=2
END=48

LOGFILE_PREFIX="benchmark"
NORMAL_TIME=230

for i in `seq -f "%03g" ${START} ${END}`
do
  CPU_UTIL=`ssh gpu$i top -bn 2 -d 0.01 | grep 'Cpu' | tail -n 1 \
    | gawk '{print $2+$4+$6}'`
  if [ `echo "${CPU_UTIL} < 75.0" | bc` -eq 1 ]; then
    LOGFILE_NAME=${LOGFILE_PREFIX}_gpu$i.log
    echo "running on gpu queue with machine gpu$i" > ${LOGFILE_NAME}
    ssh gpu$i sysbench --test=cpu --cpu-max-prime=20000 \
      --num_threads=1 run >> ${LOGFILE_NAME} &
  fi
done

# WAIT FOR TASKS DONE
sleep ${NORMAL_TIME}

# OUTPUT RESULT
grep -Hnr "total time:" benchmark_gpu*.log | sort

