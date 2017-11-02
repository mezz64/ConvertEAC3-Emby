##A docker to convert your videos with EAC3 audio to AC3 audio

Container automatically checks with Emby every 10 minutes to see if any EAC3 audio files exist in the library.  If files are found the audio is converted to AC3 and the existing file is replaced.

Configuration is done via the following enviroment variables:
- EMBY_URL: Full path to your emby instance. (Ex. http://192.1.1.10:8096)
- EMBY_API_KEY: API key with permissions to connect to the server.
- EMBY_USER_KEY: Key of the user id you'd like to use to make the file information requests.
- EMBY_UNC: UNC root path to your media, if applicable.  This is needed to properly automatic replacement of the existing files since Emby stores media paths as fully qualifed UNC paths, not local paths.

Mount points are available for the following container paths:
- /config: Log files and temporary files used during conversion will be stored here.
- /tv_mnt: This should point to the local root of your media directory.

Networking access is required to connect to the emby server.


Docker run command example:
`docker run  --net="bridge" -e "EMBY_URL"="http://192.1.1.10:8096" -e "EMBY_API_KEY"="YOUR_API_KEY" -e "EMBY_USER_KEY"="YOUR_USER_KEY" -e "EMBY_UNC"="//192.1.1.10" -v "/config_path":"/config" -v "/local_path":"/tv_mnt" mezz64/converteac3-emby`

Docker hub link: https://hub.docker.com/r/mezz64/converteac3-emby/
