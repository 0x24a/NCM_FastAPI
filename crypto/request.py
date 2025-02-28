from typing import Literal
from random import randint, choice
from time import time
import httpx
from crypto.encrypt import we_encrypt, e_encrypt, linux_encrypt

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
    "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89;GameHelper",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1",
    "Mozilla/5.0 (iPad; CPU OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1",
    "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BKK-AL10 Build/HONORBKK-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/10.6 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/13.10586",
]  # https://github.com/Kevin0z0/Python_NetEaseMusicAPI/blob/master/api/utils/send.py, Line 9-26


class NCMRequest:
    def __init__(
        self,
        method: Literal["GET", "POST"],
        url: str,
        data: dict = {},
        cookies: dict = {},
        encryption: Literal["we_encrypt", "e_encrypt", "linux_encrypt"] = "we_encrypt",
        *args,
        **kwargs
    ) -> None:
        self.method = method
        self.url = url
        self.data = data
        self.cookies = cookies
        self.encryption = encryption
        self.args = args
        self.kwargs = kwargs
        self.headers = {
                    "User-Agent": choice(USER_AGENTS),
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": "https://music.163.com/"
                }
    
    def _generate_request_url(self, url: str) -> str:
        if not url:
            return "https://music.163.com/api/linux/forward"
        elif url.startswith("http"):
            return url
        else:
            return "https://music.163.com/" + url
    
    def _encrypt_payload(self, payload: dict) -> dict:
        match self.encryption:
            case "linux_encrypt":
                self.headers["User-Agent"] = USER_AGENTS[0]
                payload["method"] = "POST"
                return linux_encrypt(payload)
            case "we_encrypt":
                payload["csrf_token"] = self.cookies["__csrf"] if "__csrf" in self.cookies else ""
                return we_encrypt(payload)
            case "e_encrypt":
                payload["header"] = {
                    'osver': "",
                    "appver": "8.0.0",
                    "channel": "",
                    "deviceId": "",
                    "mobilename": "",
                    "os": "android",
                    "resolution": "1920x1080",
                    "versioncode": "140",
                    "buildver": str(int(time())),
                    "requestId": str(int(time()*100))+"_0"+str(randint(100, 999)),
                    "__csrf": self.cookies["__csrf"] if "__csrf" in self.cookies else ""
                }
                if "MUSIC_U" in self.cookies: payload["header"]["MUSIC_U"] = self.cookies["MUSIC_U"]
                if "MUSIC_A" in self.cookies: payload["header"]["MUSIC_A"] = self.cookies["MUSIC_A"]
                self.headers["Cookie"] = ''.join(map(lambda key: f"{key}={payload['header'][key]};",payload["header"]))
                return e_encrypt(self.url, payload)
            case _:
                raise ValueError(f"Unknown encryption type: {self.encryption}")
    
    def send(self) -> httpx.Response:
        if self.method == "GET":
            if self.encryption == "e_encrypt":
                self.headers["User-Agent"] = USER_AGENTS[-1]
            response = httpx.get(
                self._generate_request_url(self.url),
                headers=self.headers,
                cookies=self.cookies,
                *self.args,
                **self.kwargs
            )
        elif self.method == "POST":
            response = httpx.post(
                self._generate_request_url(self.url),
                headers=self.headers,
                data=self._encrypt_payload(self.data),
                cookies=self.cookies,
                *self.args,
                **self.kwargs
            )
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        return response
            
        