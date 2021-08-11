from time import sleep
import pandas as pd
from crawlers.utils import get_external_ip
from .utils import *


class VpnGate:
    def __init__(self):
        self.prev_ip = []
        self.process = None

    def connect_server(self, try_n=3, wait_sec=10):
        self.disconnect()
        current_ip = get_external_ip()
        path_ovpn = saveOvpn(self.get_server())
        self.process = connect(path_ovpn)

        try_cnt = 0
        while current_ip != get_external_ip():
            sleep(wait_sec)
            if try_cnt > try_n:
                break
            try_cnt +=1
    
    def disconnect(self, wait_sec=0.5):
        if self.process != None:
            self.process.terminate()
            sleep(wait_sec)

    def get_server(self):
        server = dict()
        while not server or server.get('IP', '') in self.prev_ip:
            server = self.__get_server()
        self.prev_ip.append(server.get('IP'))
        return server

    def __get_server(self):
        servers = getServers()
        servers = pd.DataFrame(servers)
        servers = servers[~servers.IP.isin(self.prev_ip)]
        servers = servers.sort_values(by='Speed', ascending=False).iloc[:30].sample(1)
        server = list(servers.T.to_dict().values())[0]
        return server
