import requests
import os
import sys
import tarfile
import shutil
import yaml
from sys import exit
from time import sleep

latestVersion = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
baseUrl = "https://ddragon.leagueoflegends.com/cdn/dragontail-{}.tgz".format(latestVersion)

def download(url, filename):
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}] ({})'.format('█' * done, '.' * (50-done), f"{round(downloaded/1000000)}MB/{round(total/1000000)}MB"))
                sys.stdout.flush()
    sys.stdout.write('\n')
print("Checking for Updates...")

if os.path.isfile('info.yml'):
    with open('info.yml', 'r') as file:
        fileData = yaml.safe_load(file)
        if fileData['Assets_Version'] != latestVersion:
            print("New Version Assets Found", latestVersion)
        else:
            print("Your on Latest Version!")
            exit(0)
print(f"Downloading dragontail-{latestVersion}.tgz from {baseUrl}")
download(baseUrl, f"dragontail-{latestVersion}.tgz")
if os.path.isdir("DDragon"):
    print("Deleting Older files")
    shutil.rmtree(r'DDragon')
else:
    os.mkdir("DDragon")
print("Unpacking")
with tarfile.open(f"dragontail-{latestVersion}.tgz", 'r') as tar:
    for item in tar:
        tar.extract(item, "DDragon")
print("Done")
print(f"deleting dragontail-{latestVersion}.tgz")
sleep(5)
os.remove(f"dragontail-{latestVersion}.tgz")
print("Configuring...")
infoFile = {'Name': 'TPLoLPlugin', 'Author': 'xXKiller_BOSSXx', 'Website': 'https://github.com/KillerBOSS2019', 'Assets_Version': latestVersion, 'PluginVersion': 2.0}

with open('info.yml', 'w') as file:
    yaml.dump(infoFile, file)
print("Done!")

input()
