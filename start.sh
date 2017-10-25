#!/bin/bash

#Give message when starting the container
printf "\n \n \n ------------------------Starting container ------------------------ \n \n \n"

# Configure user nobody to match unRAID's settings
#export DEBIAN_FRONTEND="noninteractive"
usermod -u 99 nobody
usermod -g 100 nobody
usermod -d /home nobody
chown -R nobody:users /home

#chsh -s /bin/bash nobody

#cp /converteac3.sh /config/converteac3.sh
#chown -R nobody:users /config


#if [ -n "$EMBY_URL" ]; then
#  sed -i "s/^  ha_url:.*/  ha_url: $(echo $HA_URL | sed -e 's/\\/\\\\/g; s/\//\\\//g; s/&/\\\&/g')/" $CONF/appdaemon.yaml
#fi

# Start program
emby_eac3.py $EMBY_API_KEY $EMBY_USER_KEY $EMBY_URL $EMBY_UNC

#echo "[Info] Starting script"

#bash /config/converteac3.sh
#su - nobody -c /config/converteac3.sh

echo "Stopping Container.."
