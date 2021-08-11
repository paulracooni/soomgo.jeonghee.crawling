import requests, base64, tempfile, subprocess

OPENVPN_PATH = "openvpn"
VPNGATE_API_URL = "http://www.vpngate.net/api/iphone/"
DEFAULT_COUNTRY = "US"
SELECTED_COUNTRY = ""
DEFAULT_SERVER = 0
YES = False

def getServers():
    servers = []
    server_strings = requests.get(VPNGATE_API_URL).text
    for server_string in server_strings.replace("\r", "").split('\n')[2:-2]:

        (
            HostName, IP, Score, Ping, Speed, CountryLong, CountryShort, NumVpnSessions,
            Uptime, TotalUsers, TotalTraffic, LogType, Operator, Message, OpenVPN_ConfigData_Base64
        ) = server_string.split(',')

        server = {
            'HostName': HostName,
            'IP': IP,
            'Score': Score,
            'Ping': Ping,
            'Speed': Speed,
            'CountryLong': CountryLong,
            'CountryShort': CountryShort,
            'NumVpnSessions': NumVpnSessions,
            'Uptime': Uptime,
            'TotalUsers': TotalUsers,
            'TotalTraffic': TotalTraffic,
            'LogType': LogType,
            'Operator': Operator,
            'Message': Message,
            'OpenVPN_ConfigData_Base64': OpenVPN_ConfigData_Base64
        }

        servers.append(server)
    return servers

def saveOvpn(server):
    _, ovpn_path = tempfile.mkstemp()
    ovpn = open(ovpn_path, 'w')
    ovpn.write(base64.b64decode(server["OpenVPN_ConfigData_Base64"]).decode())
    ovpn.write('\nscript-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf')
    ovpn.close()
    return ovpn_path

def connect(ovpn_path):
    return subprocess.Popen([OPENVPN_PATH, '--config', ovpn_path])

