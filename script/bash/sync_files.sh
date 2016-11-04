#!/bin/bash
#
# Perform automatic sync service over local and remote
# UNCOMMENT THIS WHILE DEBUGGING: set -x

declare -a REMOTE_LOCATIONS_ARRAY=()
declare -a LOCAL_LOCATIONS_ARRAY=()

# Set Global Parameters HERE
# Examples:
#  Note for all PREFIX variables, strip the slashes '/'.
#   REMOTE_PREFIX=marcc:/home-4/yliu120@jhu.edu/scratch
#   LOCAL_PREFIX=/nfs/fs/amzel3/yliu120
#   SLEEP_TIME=172800

REMOTE_PREFIX=
LOCAL_PREFIX=
SLEEP_TIME=172800

SYNC_JOB_NUM=1

register_entry() {
  REMOTE_LOCATIONS_ARRAY[${SYNC_JOB_NUM}]=$1
  LOCAL_LOCATIONS_ARRAY[${SYNC_JOB_NUM}]=$2
  ((SYNC_JOB_NUM++))
}

run_sync() {
  for ((i=1;i<SYNC_JOB_NUM;i++)); do
    (rsync -rvlt ${REMOTE_PREFIX}/${REMOTE_LOCATIONS_ARRAY[$i]} \
      ${LOCAL_PREFIX}/${LOCAL_LOCATIONS_ARRAY[$i]}/ &)
  done
}

# HERE -- Add new entry -- HERE
# Examples:
#  Note: no slashes at the end of all string parameters.
#   register_entry "pi3k_new" ""
register_entry "" ""

for ((;;)) do
  run_sync
  sleep ${SLEEP_TIME} # sleep two days until next sync.
done
