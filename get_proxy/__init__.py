import ssl
import requests 
from fake_headers import Headers
from datetime import datetime
from tqdm import tqdm 
from typing import List
import json 


class Proxy:
    
    def __init__(self,
                 ip=None,
                 port=None, 
                 country_code=None, 
                 ssl_support=False,
                 google_passed=False,
                 response_time=None):
        self.ip = ip
        self.port = port
        self.country_code = country_code
        self.ssl_support = ssl_support
        self.google_passed = google_passed
        self.is_active = False
        self.use_count = 0
        self.response_time = response_time

    @classmethod
    def set_from_row(cls, row):
        properties = row.split(' ')
        proxy = cls()
        ip_address = properties[0].split(':')
        proxy.ip = ip_address[0]
        proxy.port = ip_address[1]
        extra_properties = properties[1].split('-')
        proxy.country_code = extra_properties[0]
        if len(extra_properties)>2:
            if '!' not in extra_properties[2]:
                proxy.ssl_support = True
        if len(properties) > 2 and properties[2] == '+':
            proxy.google_passed = True

        return proxy 
    
    def to_dict(self) -> dict:
        return {'https': f"{self.ip}:{self.port}",'http': f"{self.ip}:{self.port}"}
        
    @classmethod
    def none_dict(cls) -> dict:
        return {'http' : None, 'https': None}
    
    def __str__(self) -> str:
        return f"{self.ip}:{self.port}"
    
    def obj_dict(self):
        obj = self.__dict__
        obj["response_time"] = str(obj["response_time"])
        return obj
        
    
class ProxyList: 
    _list = None
    _fail_list = None
    _last_used = None
    def __init__(self):
        self._list = [] 
        self._fail_list = [] 

    def __init__(self) -> None:
        self._list = []
        self._fail_list = [] 
        
    @property
    def length(self):
        return len(self._list)

    def set_inactive(self, index : int) -> None:
        if self._list[index]:
            self._list[index].active = False

    def _is_active_spys(self, proxy):
        return True 


    def add(self, proxy : Proxy, check_duplicates=True) -> None:
        exist = False
        if check_duplicates:
            for proxy_in_list in self._list:
                if str(proxy_in_list) == str(proxy):
                    exist = True
                    break
            
        if not exist:
            proxy.id = self.length
            self._list.append(proxy)

    def get(self, country_code: list=None, ssl_support :bool=None, google_passed:bool=None, use_limit :int=0) -> Proxy:
        proxy =  self.filter(
            country_code,
            ssl_support,
            google_passed,
            use_limit,
        )[0]
        proxy.use_count += 1
        self._last_used = proxy
        return proxy
    
    @property
    def first(self) -> Proxy:
        return self._list[0]
    
    @property
    def last_used(self) -> Proxy:
        return self._last_used

    @property
    def next(self) -> Proxy:
        next_id = 0
        if self.last_used:
            next_id = self._last_used.id + 1
        if self.length >= next_id:
            self._last_used = self._list[next_id]
            return self._list[next_id]
        raise ValueError

    def filter(self, country_code: list=None, ssl_support :bool=None, google_passed:bool=None, use_limit :int=0) -> list:
        
        return_list = [proxy for proxy in self._list if proxy.is_active]
        
        if country_code:
            # TODO filter country_code 
            pass  
        
        if ssl_support:
            return_list = [proxy for proxy in return_list if proxy.ssl_support]
            
        if use_limit:
            return_list = [proxy for proxy in return_list if proxy.use_count < use_limit]
            
        if google_passed:
            return_list = [proxy for proxy in return_list if proxy.google_passed]
        
        
        if not len(return_list):
            raise Exception("Proxy list empty")
        
        return return_list

    def count(self, country_code: list=None, ssl_support :bool=None, google_passed:bool=None, use_limit :int=0) -> int:
        return len(self.filter(country_code, ssl_support, google_passed, use_limit))

    def add_fail_list(self, proxy : Proxy=None):
        if proxy:
            self._fail_list.append(proxy)
    
    @property
    def all(self) -> List[Proxy]:
        return self._list


class GetProxy:
    _ip_address = None
    _last_check_time : datetime = None
    _proxy_list : ProxyList = None
    _header = None
    _use_tqdm = True
    get_proxies_method = ["spys"]
    check_proxies_method = "ipify"
    save_as_method = "json"
    timeout = 5
    limit = 10000
    
    def __init__(self, 
                proxy_list = ProxyList,
                use_tqdm=True,
                check_duplicates = True,
                timeout= 5,
                limit = 10000,
                check=True,
                checker="ipify"
                ):
        """
        You can set your own proxylist \n 
        checker: string --> ipify or heroku 
        """
        self._use_tqdm = use_tqdm
        self._proxy_list = proxy_list()
        self.timeout = 5
        self.limit = limit
        self._header = Headers().generate() 
        self.check = check
        self.check_proxies_method = checker
        
        
        self.get_proxies()
        
        
    def check_proxy(self, proxy: Proxy=None) -> bool:
        """
            Checks if proxy active. If you changed your checking method you dont need to override this method 
            you can easily add new is_active method check documentation  
        """
        
        if not self.check:
            return True
        
        attr_name = f"check_proxy_{self.check_proxies_method}"
        if not hasattr(self, attr_name):
            raise Exception(f"{attr_name} method does not exist")
        
        check_proxy_attr = getattr(self,attr_name)
        
        if not proxy:
            self._ip_address = check_proxy_attr(Proxy.none_dict())
            return 

        proxy_ip = check_proxy_attr(proxy.to_dict())
        return self._ip_address != proxy_ip
    
    def check_proxy_heroku(self, proxy_dict) -> str:
        return requests.get("https://check-my-ip.herokuapp.com/", timeout=self.timeout, proxies=proxy_dict).json()["ip"]
    
    def check_proxy_ipify(self, proxy_dict) -> str:
        return requests.get("https://api.ipify.org?format=json", timeout=self.timeout, proxies=proxy_dict).json()["ip"]
   
    def get_proxies(self):
        """
            Getting proxies from source url, if you want to change your proxy source you have to override this method 
            NOTE the only thing you have to do is filling proxy_list 
        """
        for get_proxy_method in self.get_proxies_method:
            proxy_source_attr_name = f"get_from_{get_proxy_method}"
            if not hasattr(self, proxy_source_attr_name):
                raise Exception(f"{proxy_source_attr_name} method does not exist")
            
            self._last_check_time = datetime.now()
            proxies = getattr(self, proxy_source_attr_name)() # expects list[Proxy] 
            
            self.check_proxy() # To get ip adress 
            for proxy in tqdm(proxies[:self.limit]):
                try:
                    d1 = datetime.now()
                    proxy.is_active = self.check_proxy(proxy)
                    proxy.response_time = datetime.now() - d1
                    self._proxy_list.add(proxy=proxy, check_duplicates=True)
                except Exception:
                    self._proxy_list.add_fail_list(proxy)

    def get_from_spys(self) -> List[Proxy]:
        proxies = str(requests.get("http://spys.me/proxy.txt").content).split("\\n")[9:-2]
        return [Proxy.set_from_row(proxy) for proxy in proxies]
        
    @property
    def ip_address(self) -> str:
        return self._ip_address
            
    @property
    def list(self) -> ProxyList:
        return self._proxy_list
    
    def save(self, country_code: list=None, ssl_support :bool=None, google_passed:bool=None, use_limit :int=0) -> None:
        attr_name = f"save_as_{self.save_as_method}"
        if not hasattr(self, attr_name.lower()):
            raise Exception(f"GetProxy dont have {attr_name} method")
        
        save_as = getattr(self, attr_name)
        save_as(self._proxy_list.filter(country_code, ssl_support, google_passed, use_limit)) # passing proxyList attribute 
        
    def save_as_json(self, proxy_list : List[Proxy] = None) -> None:
        if not proxy_list:
            proxy_list = self._proxy_list.all
        dump = json.dumps([obj.obj_dict() for obj in proxy_list])
        with open("proxy_list.json", "w+") as file:
            file.write(dump)

    @property
    def ip_address(self):
        if not self._ip_address:
            self._ip_address = self.check_proxy()
        return self._ip_address