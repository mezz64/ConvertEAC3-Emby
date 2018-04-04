#!/bin/bash

#Give message when starting the container
printf "\n \n \n ------------------------Starting container ------------------------ \n \n \n"

# Configure user nobody to match unRAID's settings
#export DEBIAN_FRONTEND="noninteractive"
usermod -u 99 nobody
usermod -g 100 nobody
usermod -d /home nobody
chown -R nobody:users /home

# Start program
python emby_eac3.py $EMBY_API_KEY $EMBY_USER_KEY $EMBY_URL $EMBY_UNC

echo "Stopping Container.."
