#!/bin/bash

# Variables from environement
: "${SALT_NAME:=minion}"
: "${LOG_LEVEL:=info}"
: "${OPTIONS:=}"

echo $SALT_NAME > /etc/salt/minion_id

# Set salt grains
if [ ! -z "$SALT_GRAINS" ]; then
    echo "INFO: Set grains on $SALT_NAME to: $SALT_GRAINS"
    echo $SALT_GRAINS > /etc/salt/grains
fi

echo "INFO: Starting salt-minion with log level $LOG_LEVEL with hostname $SALT_NAME"
echo "log_level: ${LOG_LEVEL}" > /etc/salt/minion.d/logging.conf
/usr/bin/salt-minion
