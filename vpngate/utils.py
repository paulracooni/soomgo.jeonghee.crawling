import requests, json, sys, base64, tempfile, subprocess, time

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

def getCountries(server):
    return set((server['CountryShort'], server['CountryLong']) for server in servers)

def printCountries(countries):
    print("    Connectable countries:")
    newline = False
    for country in countries:
        print("    %-2s) %-25s" % (country[0], country[1])),
        if newline:
            print('\n'),
        newline = not newline
    if newline:
        print('\n'),

def printServers(servers):
    print("  Connectable Servers:")
    for i in xrange(len(servers)):
        server = servers[i]

        ipreq = requests.get("https://ipinfo.io/%1s" % (server['IP']))
        ipinfo = json.loads(ipreq.text)

        print("    %2d) %-15s [%6.2f Mbps, ping:%4s ms, score: %3s, hostname: %4s," % (i,
                                                                        server['IP'],
                                                                        float(server['Speed'])/10**6,
                                                                        server['Ping'],
                                                                        server['Score'],
                                                                        ipinfo['hostname']))

        print("                          city: %1s, region: %2s, org: %3s ]\n" % (ipinfo['city'], ipinfo['region'], ipinfo['org'].split(' ', 1)[1]))

def selectCountry(countries):
    selected = SELECTED_COUNTRY
    default_country = DEFAULT_COUNTRY
    short_countries = list(country[0] for country in countries)
    if not default_country in short_countries:
        default_country = short_countries[0]
    if YES:
        selected = default_country
    while not selected:
        try:
            selected = raw_input("[?] Select server's country to connect [%s]: " % (default_country, )).strip().upper()
        except:
            print("[!] Please enter short name of the country.")
            selected = ""
        if selected == "":
            selected = default_country
        elif not selected in short_countries:
            print("[!] Please enter short name of the country.")
            selected = ""
    return selected

def selectServer(servers):
    selected = -1
    default_server = DEFAULT_SERVER
    if YES:
        selected = default_server
    while selected == -1:
        try:
            selected = raw_input("[?] Select server's number to connect [%d]: " % (default_server, )).strip()
        except:
            print("[!] Please enter vaild server's number.")
            selected = -1
        if selected == "":
            selected = default_server
        elif not selected.isdigit() or int(selected) >= len(servers):
            print("[!] Please enter vaild server's number.")
            selected = -1
    return servers[int(selected)]

def saveOvpn(server):
    _, ovpn_path = tempfile.mkstemp()
    ovpn = open(ovpn_path, 'w')
    ovpn.write(base64.b64decode(server["OpenVPN_ConfigData_Base64"]).decode())
    ovpn.write('\nscript-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf')
    ovpn.close()
    return ovpn_path

def connect(ovpn_path):
    return subprocess.Popen([OPENVPN_PATH, '--config', ovpn_path])

def _connect(ovpn_path):
    openvpn_process = subprocess.Popen([OPENVPN_PATH, '--config', ovpn_path])
    try:
        while True:
            time.sleep(600)
    # termination with Ctrl+C
    except:
        try:
            openvpn_process.kill()
        except:
            pass
        while openvpn_process.poll() != 0:
            time.sleep(1)
        print("[=] Disconnected OpenVPN.")