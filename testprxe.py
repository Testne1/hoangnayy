import requests
import os
from bs4 import BeautifulSoup
import sys
import concurrent.futures
from colorama import Fore
from threading import Thread
import time

# Đường dẫn cho tập tin lưu trữ proxy
file_path = 'test.txt'
luu = 'proxies.txt'

# Kiểm tra xem tệp đã tồn tại chưa, nếu có thì xóa
if os.path.exists(file_path):
    os.remove(file_path)
if os.path.exists(luu):
    os.remove(luu)


# Lấy thông tin từ https://free-proxy-list.net/
url1 = 'https://free-proxy-list.net/'

# Mở tệp để ghi thông tin proxy vào
with open(file_path, 'a') as file:
    # Yêu cầu nội dung của trang web
    response = requests.get(url1)

    # Phân tích cú pháp HTML với BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lấy các hàng chứa thông tin proxy
    rows = soup.select('table tbody tr')

    # Lặp qua các hàng và ghi thông tin proxy vào tệp
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].get_text()
            port = cols[1].get_text()

            # Ghi thông tin proxy vào tệp
            file.write(f"{ip}:{port}\n")

    print("Đã lưu thông tin proxy từ free-proxy-list.net vào tệp", file_path)

# Lấy thông tin từ https://hidemy.name/en/proxy-list/
url2 = 'https://hidemy.name/en/proxy-list/'

# Mở tệp để ghi thông tin proxy vào
with open(file_path, 'a') as file:
    # Yêu cầu nội dung của trang web
    response = requests.get(url2)

    # Phân tích cú pháp HTML với BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lấy các hàng chứa thông tin proxy
    rows = soup.select('table tbody tr')

    # Lặp qua các hàng và ghi thông tin proxy vào tệp
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 7:
            ip = cols[0].get_text()
            port = cols[1].get_text()

            # Ghi thông tin proxy vào tệp
            file.write(f"{ip}:{port}")

    print("Đã lưu thông tin proxy từ hidemy.name/en/proxy-list/ vào tệp", file_path)

# Lấy thông tin từ https://www.sslproxies.org/
url3 = 'https://www.sslproxies.org/'

# Mở tệp để ghi thông tin proxy vào
with open(file_path, 'a') as file:
    # Yêu cầu nội dung của trang web
    response = requests.get(url3)

    # Phân tích cú pháp HTML với BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lấy các hàng chứa thông tin proxy
    rows = soup.select('table tbody tr')

    # Lặp qua các hàng và ghi thông tin proxy vào tệp
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].get_text()
            port = cols[1].get_text()

            # Ghi thông tin proxy vào tệp
            file.write(f"{ip}:{port}\n")

    print("Đã lưu thông tin proxy từ www.sslproxies.org vào tệp", file_path)
    
# Lấy thông tin từ https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all
url4 = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'

# Mở tệp để ghi thông tin proxy vào
with open(file_path, 'a') as file:
    # Yêu cầu nội dung của trang web
    response = requests.get(url4)

    # Ghi thông tin proxy vào tệp
    file.write(response.text)

    print("Đã lưu thông tin proxy từ api.proxyscrape.com vào tệp", file_path)

# Đọc danh sách proxy từ tệp
with open(file_path) as f:
    lines = f.readlines()

# Loại bỏ các dòng trống khỏi danh sách
lines = [line.strip() for line in lines if line.strip()and(line.strip().find(".") != -1)and(line.strip().find("-") == -1)]

# Ghi các dòng không trống vào tệp mới
with open('test.txt', 'w') as f:
    f.write('\n'.join(lines))

def run():
    os.system('cls' if os.name == 'nt' else 'clear')    
    def runc(proxy):
        try:
            testing = requests.get('http://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=3).json()
            print('LIVE > ' + proxy)
            open(luu, 'a').write(proxy + '\n')
        except:
            print('DIE > ' + proxy)
    def process_file(file_pa):
        with open(file_path) as f:
            proxies = f.read().split('\n')
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(runc, proxies)  
    thread = Thread(target=process_file, args=(file_path,))
    thread.start()
    thread.join()
run()
time.sleep(5)
    # Đọc danh sách proxy từ tệp
with open(luu) as f:
    lines = f.readlines()

# Loại bỏ các dòng trống khỏi danh sách
    lines = [line.strip() for line in lines if line.strip()and(line.strip().find(".") != -1)and(line.strip().find("-") == -1)]

# Ghi các dòng không trống vào tệp mới
with open('proxies.txt', 'w') as f:
    f.write('\n'.join(lines))
    print('da loc xong')