<?php
/* Period for updating */
$PERIOD = 180;

/* Querying the remote and write the remote json stats to a temp file */
function query() {
  $remote_stat = shell_exec('ssh -o ControlMaster=no marcc ./job_stat.py');

  if ($remote_stat == NULL) {
    /* keep the main loop running until the network resumes. */
    return;
  }

  /* Non failure case */
  $fp = fopen('/tmp/job_status', 'w');

  while (!flock($fp, LOCK_EX));

  fwrite($fp, $remote_stat);
  flock($fp, LOCK_UN);
  fclose($fp);
}

while(True) {
  query();

  /* query every 3 minutes */
  sleep($PERIOD);
}
?>
