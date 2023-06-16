import os
import sys
import requests
import concurrent.futures
from colorama import Fore
from threading import Thread
def run():
    os.system('cls' if os.name == 'nt' else 'clear')    
    def runc(proxy):
        try:
            testing = requests.get('http://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=3).json()
            print(f'{Fore.WHITE} [\033[1;32mLIVE{Fore.WHITE}] > ' + proxy)
            open(luu, 'a').write(proxy + '\n')
        except:
            print(f'{Fore.WHITE} [{Fore.RED}DIE{Fore.WHITE}] > ' + proxy)
    def process_file(filename):
        with open(filename) as f:
            proxies = f.read().split('\n')
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(runc, proxies)
    filename = input('Nhập Files Chứa Proxy: ')
    luu = input('Nhập Files Lưu Proxy Live: ')  
    thread = Thread(target=process_file, args=(filename,))
    thread.start()
    thread.join()
run()
