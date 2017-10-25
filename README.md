##A docker to convert your videos with EAC3 audio to AC3 audio

When you start the container, it will start the script, and stop when the script is finished. 
So you will need to restart the container when you add a file you want to convert 
You will need to place the videos you want to convert, in the appdata folder (/config). 

Thanks to bjonness406 for the docker base.

Docker run command:

`docker run -v /Path-to-config:/config mezz64/ConvertEAC3`

Docker hub link: https://hub.docker.com/r/mezz64/ConvertEAC3/
