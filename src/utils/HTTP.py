import psutil
import requests
import base64

class Http:
    def __init__(self):
        def get_lockfile():
            for ids in psutil.pids():
                try:
                    p = psutil.Process(ids)
                except:
                    continue
                try:
                    if p.name() == 'LeagueClientUx.exe':
                        with open(f'{p.exe().replace(p.name(), "lockfile")}', 'r') as file:
                            return file.read().split(':')
                except:
                    pass
            return None
        self.lockfile = get_lockfile()
        if self.lockfile != None:
            self.headers = {
                'Authorization': f'Basic {base64.b64encode(f"riot:{self.lockfile[3]}".encode("utf-8")).decode("utf-8")}'
                }
            self.verify = "riotgames.pem"
    def get(self, endpoint, json=None):
        if self.lockfile != None:
            return requests.get(f"https://127.0.0.1:{self.lockfile[2]}{endpoint}", headers=self.headers, verify=self.verify, json=json)
    def post(self, endpoint, json=None):
        if self.lockfile != None:
            return requests.post(f"https://127.0.0.1:{self.lockfile[2]}{endpoint}", headers=self.headers, verify=self.verify, json=json)
    def put(self, endpoint, json=None):
        if self.lockfile != None:
            return requests.put(f"https://127.0.0.1:{self.lockfile[2]}{endpoint}", headers=self.headers, verify=self.verify, json=json)
    def delete(self, endpoint, json=None):
        if self.lockfile != None:
            return requests.delete(f"https://127.0.0.1:{self.lockfile[2]}{endpoint}", headers=self.headers, verify=self.verify, json=json)
    def patch(self, endpoint, json=None):
        if self.lockfile != None:
            return requests.patch(f"https://127.0.0.1:{self.lockfile[2]}{endpoint}", headers=self.headers, verify=self.verify, json=json)