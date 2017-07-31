FROM debian:stretch

ARG version=2017.7
ARG salt_user=test
ARG salt_user_password=test

ENV SALT_USER $salt_user
ENV SALT_USER_PASSWORD $salt_user_password
ENV VERSION $version

# Install salt
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y wget apt-utils gnupg && \
    wget -O - https://repo.saltstack.com/apt/debian/9/amd64/latest/SALTSTACK-GPG-KEY.pub | apt-key add - && \
    echo "deb http://repo.saltstack.com/apt/debian/9/amd64/${VERSION} stretch main" > /etc/apt/sources.list.d/saltstack.list && \
    DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y salt-master salt-api salt-minion

# Customize
RUN useradd -ms /bin/bash ${SALT_USER} && \
    echo "${SALT_USER}:${SALT_USER_PASSWORD}" | chpasswd && \
    mkdir -p /var/cache/salt /var/cache/salt/master /var/cache/salt/master/jobs /var/run/salt /var/run/salt/master /etc/salt/master.d && \
    chmod 755 /var/cache/salt /var/cache/salt/master /var/cache/salt/master/jobs /var/run/salt /var/run/salt/master  /etc/salt/master.d && \
    echo "publisher_acl:" > /etc/salt/master.d/acl.conf && \
    echo "  ${SALT_USER}:" >> /etc/salt/master.d/acl.conf && \
    echo "    - .*" >> /etc/salt/master.d/acl.conf && \
    echo "external_auth:" > /etc/salt/master.d/auth.conf && \
    echo "  pam:" >> /etc/salt/master.d/auth.conf && \
    echo "    ${SALT_USER}:" >> /etc/salt/master.d/auth.conf && \
    echo "      - .*" >> /etc/salt/master.d/auth.conf

# Clean image
RUN apt-get -yqq clean && \
    apt-get -yqq purge && \
    rm -rf /tmp/* /var/tmp/* && \
    rm -rf /var/lib/apt/lists/*

# Add config files
COPY master /etc/salt/

# Entry point
ADD start.sh /start.sh
CMD ["bash", "start.sh"]
