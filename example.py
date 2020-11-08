# Tests 
from get_proxy import GetProxy, Proxy, ProxyList
import requests 
import base64 
from typing import List 
    
class ExtendedGetProxy(GetProxy):
    check_proxies_method = "spys"
    # based on attribute name check_proxy_{check_proxies_method}
    def check_proxy_spys(self, proxy_dict : dict) -> str:
        """
        Make sure you have proxy_dict as param
        proxy_dict = {'http': 'ip_address:port', 'https': 'ip_address:port'}
        
        To check ip address without proxy, proxy_dict = {'http': None, 'https': None'}
        
        """
        content, decoded_content = None, None
        try:
            url = "http://spys.me/"
            content = requests.get(url, proxies=proxy_dict).text.split("<br>")[1]
            decoded_content = str(base64.b64decode(content))
            ip_address = decoded_content.split('\\n')[5].split(" = ")[1].strip()
            return ip_address
        except Exception:
            raise Exception(content, decoded_content)
    
    get_proxies_method = ["spys", "extended"] # It should be an array 
    # based on attribute name get_from_{get_proxies_method}
    def get_from_extended(self) -> List[Proxy]:
        """
            Method should return List[Proxy] and it will use in GetProxy.get_proxies 
        """
        pass 
    
    save_as_method = "txt" 
    # based on attribute name save_as_{save_as_method}
    def save_as_txt(self, proxy_list : ProxyList) -> None:
        # save method will pass ProxyList 
        pass 
        

# get_proxy = ExtendedGetProxy(timeout=10, check_duplicates=False) # Will use get_from and check_proxy methods 


# Default Usage 

get_proxy = GetProxy(use_tqdm=True, check_duplicates= True, timeout=10, limit=5)
proxy_list = get_proxy.list # Returns ProxyList 
print(proxy_list.length)
proxy_list.all # Returns List[Proxy] 
proxy_list.filter() # country_code: list=None, ssl_support :bool=None, google_passed:bool=None, use_limit :int=0
proxy_list.get().to_dict() # country_code: list=None, ssl_support :bool=None, google_passed:bool=None, use_limit :int=0
print(proxy_list.first.to_dict())
print(proxy_list.last_used.to_dict()) 
print(proxy_list.next.to_dict())


get_proxy.save() # To save

