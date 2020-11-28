# get-proxy
Get free proxies easily, use them in your project.

### Installation

    pip install git+https://github.com/tarikyayla/get-proxy
**or**
```shell
git clone https://github.com/tarikyayla/get-proxy
cd get-proxy
python setup.py install
```
# Usage

```python
from get_proxy import GetProxy


get_proxy = GetProxy(use_tqdm=True, check=True check_duplicates= True, timeout=10, limit=5)

# You can disable checking 
get_proxy = GetProxy(use_tqdm=True, check=False, check_duplicates= True, timeout=10, limit=5)

proxy_list = get_proxy.list # Returns ProxyList 

 # @params --> country_code: list=None, ssl_support :bool=None, google_passed:bool=None, use_limit :int=0
 # returns list[Proxy]
proxy_list.filter()

proxy_list.get() # returns Proxy

get_proxy.save() # To save your ProxyList. You can use same filter parameters. 
```

### Add new get_proxy method 

```python 

class ExtendedGetProxy(GetProxy):
    get_proxies_method = ["spys", "extended"] # It should be an array 
    # based on attribute name get_from_{get_proxies_method}
    def get_from_extended(self) -> List[Proxy]:
        """
            Method should return List[Proxy] and it will use in GetProxy.get_proxies 
        """
        pass 

```

### Add new save method 

```python 

class ExtendedGetProxy(GetProxy):
    save_as_method = "txt" 
    # based on attribute name save_as_{save_as_method}
    def save_as_txt(self, proxy_list : ProxyList) -> None:
        # save method will pass ProxyList 
        pass 

```

### Add new check_proxy method 

```python 
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
```