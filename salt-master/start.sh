#!/bin/bash

# Variables from environement
: "${LOG_LEVEL:=info}"
: "${OPTIONS:=}"

echo "INFO: Starting salt-master with log level $LOG_LEVEL"
echo "log_level: ${LOG_LEVEL}" > /etc/salt/master.d/logging.conf
echo "log_level_logfile: quiet" >> /etc/salt/master.d/logging.conf


# Should we start the API ?
if [ ! -z "$SALT_API" ]; then
    echo "INFO: Starting salt-api"
	/usr/bin/salt-api &
fi

/usr/bin/salt-master
