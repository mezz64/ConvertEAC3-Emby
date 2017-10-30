"""
emby eac3 episode locator
"""
import os
import sys
import time
import subprocess
import logging
import shutil
import requests

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='/config/embyac3.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

DEFAULT_HEADERS = {
    'Content-Type': "application/json",
    'Accept': "application/json"
}

AOUTCODEC = "ac3"      # Choose audio output type (ac3 only for now)
ASAMPLERATE = "640k"      # Choose audio sample rate (default 640k)
CMIXLEVEL = "0.707"         # Center channel mix level

AUDIOTRACKPREFIX = "audio ("
VIDEOTRACKPREFIX = "video ("

def convertEAC3(file_path):
    """Convert EAC3 audo to AC3 audio"""
    _LOGGER.info("Converting: " + file_path)

    name = os.path.splitext(os.path.basename(file_path))[0]

    ac3file = "/config/" + name + ".ac3"
    newfile = "/config/" + name + "_AC3.mkv"

    cmd = ['mkvmerge', '-i', file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    file_info = result.stdout.decode('utf-8')

    audio_track_id = None
    for line in file_info.split('\n'):
        if AUDIOTRACKPREFIX + "AC3/EAC3)" in line:
            audio_track_id = line.split(':')[0].split(' ')[2]
            break

    if not audio_track_id:
        _LOGGER.error("No EAC3 audio tracks found.")
        return

    logline = "EAC3 Audio Track ID: " + audio_track_id
    print(logline)
    _LOGGER.info(logline)

    cmd = ['mkvinfo', file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    file_info2 = result.stdout.decode('utf-8')

    # Extract Audio Track Section from Output
    start_audio = False
    audio_info = ""
    for line in file_info2.split('\n'):
        if "mkvextract: " + audio_track_id in line:
            start_audio = True
        if "mkvextract: " + str((int(audio_track_id) + 1)) in line:
            start_audio = False
        if start_audio:
            audio_info += line + "\n"

    # Confirm the track is EAC3
    audio_track_type = None
    for line in audio_info.split('\n'):
        if "Codec ID" in line:
            audio_track_type = line.split(':')[1]
            break

    # Try to get track language
    audio_track_lang = "eng"
    for line in audio_info.split('\n'):
        if "Language" in line:
            print("Language other than english detected.")
            # audio_track_lang = line.split(':')[1]
            break
    print("Language: " + audio_track_lang)

    # Generate AC3 Audio
    if audio_track_type == " A_EAC3":
        logline = "Generating AC3 Audio File..."
        print(logline)
        _LOGGER.info(logline)
        cmd = ['ffmpeg',
               '-drc_scale', '0',
               '-i', file_path,
               '-vn',
               '-acodec', AOUTCODEC,
               '-center_mixlev', CMIXLEVEL,
               '-ab', ASAMPLERATE,
               ac3file]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL)
    else:
        print("EAC3 Audio Track Could Not Be Verified.")
        return

    # Get ID of video track
    video_track_id = None
    for line in file_info.split('\n'):
        if VIDEOTRACKPREFIX in line:
            video_track_id = line.split(':')[0].split(' ')[2]
            break

    logline = "Video Track ID: " + video_track_id
    print(logline)
    _LOGGER.info(logline)

    # Merge files together
    logline = "Merging files back together..."
    print(logline)
    _LOGGER.info(logline)
    cmd = ['mkvmerge',
           '-o', newfile,
           '-A',
           '--compression', video_track_id+':none', file_path,
           '--language', '0:'+audio_track_lang,
           '--compression', '0:none', ac3file]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL)

    # Remove AC3 file
    logline = "Removing temporary AC3 file..."
    print(logline)
    _LOGGER.info(logline)
    try:
        os.remove(ac3file)
    except FileNotFoundError:
        _LOGGER.info("AC3 File doesn't exist, quitting.")
        return

    # Explicitly set new file permissions
    os.chown(newfile, 99, 100)

    # Overwrite existing with new file
    shutil.move(newfile, file_path)

    # We are done
    logline = "Conversion of " + name + " is complete."
    print(logline)
    _LOGGER.info(logline)
    return


def main():
    """Main function."""
    api_key = sys.argv[1]
    user_key = sys.argv[2]
    server_url = sys.argv[3]
    unc_path = sys.argv[4]

    id_dict = []

    audio_type = "EAC3"

    emby_request = requests.Session()
    emby_request.timeout = 5
    emby_request.stream = False
    emby_request.params = {'api_key': api_key}
    emby_request.headers.update(DEFAULT_HEADERS)

    list_url = server_url + "/Reports/Items?StartIndex=0&Limit=10000&IncludeItemTypes=Episode&HasQueryLimit=true&GroupBy=None&ReportView=ReportData&DisplayType=Screen&UserId=" \
        + user_key + "&SortOrder=Ascending&ReportColumns=CName%7CEpisodeSeries%7CSeason%7CEpisodeNumber%7CVideo%7CAudio%7CPath&ExportType=CSV"

    _LOGGER.info("Starting Emby Update Fetch Loop...")
    while True:
        try:
            response = emby_request.get(list_url)
        except requests.exceptions.RequestException as err:
            _LOGGER.error('Requests error getting episode list: %s', err)
            return
        else:
            episode_list = response.json()

        for episode in episode_list['Rows']:
            if episode['Columns'][4]['Name'] == audio_type:
                #print(episode['Columns'][0]['Name'] + " - " + episode['Id'] + " - " + episode['Columns'][4]['Name'])
                id_dict.append(episode['Id'])

        for epid in id_dict:
            lookup_url = server_url + "/Users/" + user_key + "/Items/" + epid
            try:
                response = emby_request.get(lookup_url)
            except requests.exceptions.RequestException as err:
                _LOGGER.error('Requests error getting episode path: %s', err)
                return
            else:
                info = response.json()

            local_path = info['MediaSources'][0]['Path'].replace("\\", "/")
            local_path = local_path.replace(unc_path, "/tv_mnt")

            print(local_path)
            _LOGGER.info(local_path)

            convertEAC3(local_path)

        # Clear dicts
        id_dict = []

        # Check every 10 minutes
        time.sleep(600)


if __name__ == '__main__':
    main()
