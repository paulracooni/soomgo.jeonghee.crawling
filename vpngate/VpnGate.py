from os import path, remove
from posixpath import basename
from time import time, sleep
import pandas as pd
from requests import exceptions
from crawlers.utils import get_external_ip
from .utils import *

DEBUG = False
PATH_BLACKLIST = path.join(path.dirname(__file__), "VPN_BLACKLIST")
class VpnGate:
    def __init__(self, verbose=True, test_url=''):
        self.prev_ip = []
        self.process = None
        self.verbose = verbose
        self.test_url = test_url

    def connect_server(self, timeout=30, max_try_n=3, try_n=0):

        self.disconnect()

        current_ip   = get_external_ip()
        path_ovpn    = saveOvpn(self.get_server())
        if self.verbose: print("Start New VPN Process")
        self.process = connect(path_ovpn)

        ptime_start = time()
        if self.verbose: print("Start VPN Connection sequences")
        while True:

            line = self.process.stdout.readline().decode().replace('\n', '')
            if self.verbose and DEBUG: print(f"{time() - ptime_start:.2f}/{timeout} -> {line}")
            sleep(0.01)

            if any([ break_line in line for break_line in [
                'Initialization Sequence Completed',
                'failed: Connection refused',
                'SIGTERM[soft,auth-failure]'
            ]]):
                break

            ptime_connect = time() - ptime_start
            if ptime_connect>timeout:
                if self.verbose: 
                    print(f"{ptime_connect:.2f}/{timeout} -> Time out!")
                break

        if self.verbose: print("End VPN Connection sequences")
        # If ip is not changed, Retry recursively
        connected_ip = get_external_ip()
        if all([connected_ip, current_ip == connected_ip, max_try_n > (try_n-1)]):

            if self.verbose:
                print(f"VPN Connection Fail>> Previous IP :{current_ip}, Current IP: {connected_ip}\n")

            connected_ip = self.connect_server(
                timeout   = timeout,
                max_try_n = max_try_n,
                try_n     = try_n + 1
            )

        elif self.verbose:

            print(f"VPN Connection Success>> Previous IP :{current_ip}, Current IP: {connected_ip}\n")

        if self.test_url:
            try:
                response = requests.get(self.test_url, timeout=15)
                if response.status_code == 429:
                    print(f"BUT! This IP({connected_ip}) has beend blocked now >> Retry\n")
                    self.put_blacklist(connected_ip)
                    connected_ip = self.connect_server(
                        timeout   = timeout,
                        max_try_n = max_try_n,
                        try_n     = try_n + 1
                    )
                elif response.status_code != 200:
                    print(f"test_url have someting wrong... (CODE:{response.status_code}) ")
            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError
            ):
                print(f"But! Time out.. ({connected_ip}) Too slow >> Retry \n")
                self.put_blacklist(connected_ip)
                connected_ip = self.connect_server(
                    timeout   = timeout,
                    max_try_n = max_try_n,
                    try_n     = try_n + 1
                )


        return connected_ip

    def disconnect(self, wait_sec=0.5):
        if self.process != None:
            self.process.terminate()
            if self.verbose: print("Terminate VPN Process")
            sleep(wait_sec)

    def get_server(self):
        server = dict()
        while not server or server.get('IP', '') in self.prev_ip:
            server = self.__get_server()
        self.prev_ip.append(server.get('IP'))
        return server

    def __get_server(self):

        blacklist = self.list_blacklist()
        servers = getServers()
        servers = pd.DataFrame(servers)
        servers = servers[~servers.IP.isin(self.prev_ip)]
        servers = servers[~servers.IP.isin(blacklist)]

        if len(servers) < 5:
            self.prev_ip = []
            self.delete_blacklist()

        # servers = servers.sort_values(by='Ping').iloc[:30].sample(1)
        servers = servers.sample(1)
        server = list(servers.T.to_dict().values())[0]
        return server

    def list_blacklist(self):
        if not path.isfile(PATH_BLACKLIST):
            return []

        with open(PATH_BLACKLIST, 'r') as f:
            blacklist = list(map(lambda b: b.replace('\n', ''), f.readlines()))

        return blacklist

    def put_blacklist(self, vpn_ip):
        with open(PATH_BLACKLIST, 'a') as f:
            print(vpn_ip, file=f)

    def delete_blacklist(self):
        remove(PATH_BLACKLIST)
