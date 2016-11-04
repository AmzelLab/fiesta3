#!/bin/bash
#
# Perform automatic sync service over local and remote

declare -a REMOTE_LOCATIONS_ARRAY=()
declare -a LOCAL_LOCATIONS_ARRAY=()

# Set Global Parameters HERE
REMOTE_PREFIX=marcc:/home-4/yliu120@jhu.edu/scratch/
LOCAL_PREFIX=/nfs/fs/amzel3/yliu120/
SYNC_JOB_NUM=1
SLEEP_TIME=172800

register_entry() {
  REMOTE_LOCATIONS_ARRAY+=$1
  LOCAL_LOCATIONS_ARRAY+=$2
  SYNC_JOB_NUM=SYNC_JOB_NUM+1
}

run_sync() {
  for ((i=1;i<SYNC_JOB_NUM;i++)); do
    rsync -rvlt ${REMOTE_PREFIX}${REMOTE_LOCATIONS_ARRAY[$i]} \
      ${LOCAL_PREFIX}${LOCAL_LOCATIONS_ARRAY[$i]}/ &
  done
}

# HERE -- Add new entry -- HERE
register_entry "pi3k_new" ""
register_entry "nis_sandwich/production" "nis_sandwich"

for ((;;)) do
  run_sync
  sleep ${SLEEP_TIME} # two days.
done
