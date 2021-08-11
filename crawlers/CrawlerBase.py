import requests
from os import path, makedirs
from vpngate.VpnGate import VpnGate
from .utils import get_user_agent, get_external_ip

class CrawlerBase:

    base_url  = ""
    debug_dir = ""
    use_vpn   = False
    vpn_gate  = VpnGate()

    def run(self):
        raise NotImplementedError

    def reset(self):
        if self.use_vpn:
            self.vpn_gate.connect_server()
        self.set_session()
        self.set_headers()
        self.set_cookies()

    def set_session(self):
        self.session = requests.Session()

    def set_headers(self):
        assert self.base_url, "Please set BASE_URL as class variable."
        self.headers = {
            'User-Agent'     : get_user_agent(),
            'connection'     : 'keep-alive',
            'referer'        : self.base_url
        }

    def set_cookies(self):
        assert self.base_url, "Please set base_url as class variable."
        assert hasattr(self, 'session'), "Must be call this after call self.set_session()"
        assert hasattr(self, 'headers'), "Must be call this after call self.set_headers()"

        response = self.session.get(self.base_url, headers=self.headers)

        if response.status_code == 200:
            self.cookies = response.cookies.get_dict()
        else:
            raise RuntimeError(
                f"Failed get cookies\n"
                f"- Status code: {response.status_code}"
            )

    def get(self, url):
        assert hasattr(self, 'session'), "Must be call this after call self.reset()"
        assert hasattr(self, 'headers'), "Must be call this after call self.reset()"
        assert hasattr(self, 'cookies'), "Must be call this after call self.reset()"
        response = self.session.get(url=url, headers=self.headers, cookies=self.cookies)
        return self.__process_response(
            response = response,
            url      = url,
            callback = self.get
        )

    def post(self, url, data=None):
        assert hasattr(self, 'session'), "Must be call this after call self.reset()"
        assert hasattr(self, 'headers'), "Must be call this after call self.reset()"
        assert hasattr(self, 'cookies'), "Must be call this after call self.reset()"
        response = self.session.post(url, data=data)
        return self.__process_response(
            response = response,
            url      = url,
            callback = self.post,
            data     = data
        )

    def __process_response(self, response, url, callback, *args, **kwargs):

        if response.status_code == 200:
            return response

        elif response.status_code == 429 and self.use_vpn:
            #@TODO: RESET VPN
            self.reset()
            return callback(url, *args, **kwargs)

        elif response.status_code == 429:
            self.save_response_as_html(
                response, name=f"ip_vaned_{response.status_code}"
            )
            raise RuntimeError(
                f"Your IP has been vanned.\n"
                f"- CODE:{response.status_code}\n"
                f"- IP:{get_external_ip()}")

        else:
            self.save_response_as_html(
                response, name=f"unexpected_{response.status_code}"
            )
            raise RuntimeError(
                f"Unexpected response\n"
                f"- CODE:{response.status_code}"
            )

    def save_response_as_html(self, response, name='Error'):

        if not self.debug_dir:
            return None

        if not path.isdir(self.debug_dir):
            makedirs(self.debug_dir, exist_ok=True)

        path_html = path.join(self.debug_dir, f"{name}.html")
        with open(path_html, "w", encoding='UTF-8') as f:
            f.write(response.text)
