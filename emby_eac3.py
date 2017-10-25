"""
emby eac3 episode locator
"""
import sys
import time
import subprocess
import logging
import requests

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='/config/embyac3.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

DEFAULT_HEADERS = {
    'Content-Type': "application/json",
    'Accept': "application/json"
}


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

    print("Starting Emby Update Fetch Loop...")
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

            cmd = ['./converteac3.sh', local_path]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            for line in p.stdout:
                print(line)
                _LOGGER.info(line)
            p.wait()

        # Clear dicts
        id_dict = []

        # Check every 10 minutes
        time.sleep(600)


if __name__ == '__main__':
    main()
