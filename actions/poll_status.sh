#!/bin/bash

# Polls a given micro service URL for current status of some long running process.
#
# Will check the HTTP server's response to determine whether or not the process
# has finished processing. It expects a JSON field called "state", and will
# continue to poll the URL as long as "state" equals "started". If e.g. "done",
# "error", or "none" is received an error is generated and the polling stops.
#
# Depends on curl and python to be able to run at the moment.

URL=$1
SLEEP=$2
STATE='"started"'
LOG=/var/log/arteria_poll.log

#echoerr() {
#       >&2 echo $@;
#}
# TODO: We might need some logging as well as return a msg when we're quiting.

if [ -z "${URL}" ] ; then
        echo "`date` -- No arguments given. Need an URL to poll." #>> $LOG
        exit 1
fi

if [[ -z "${SLEEP}" || ${SLEEP} == "None" ]] ; then
        SLEEP=1
fi

while [[ ${STATE} == '"started"' ]] ; do
        #STATUS=`curl -s -o /dev/null -w "%{http_code}" $URL`
        STATE=`curl -s ${URL} | python -m json.tool | grep state | awk '{print $2}'`

        if [[ ${STATE} != '"started"' ]] ; then
                echo "`date` -- ${URL} returned state ${STATE}. Will now stop polling the status." #>> $LOG
        fi

		# Successfully finished processing job
		if [[ ${STATE} == '"done"' ]] ; then
                exit 0
        # Some kind of error was encountered with the requested process
        # TODO: Print out the msg field?
        elif [[ ${STATE} == '"error"' || ${STATE} == '"none"' ]]; then
                exit 1
        fi

        echo "`date` -- ${URL} returned ${STATE} - sleeping ${SLEEP}m until retrying again..." #>> $LOG

        sleep ${SLEEP}m
done

exit 0
