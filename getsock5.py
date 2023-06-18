import requests

import os

from bs4 import BeautifulSoup

import sys

import concurrent.futures

from colorama import Fore

import socket

import socks

import json

file_path = 'test.txt'

luu = 'sock5.txt'

# Kiểm tra xem tệp đã tồn tại chưa, nếu có thì xóa

if os.path.exists(file_path):

    os.remove(file_path)

if os.path.exists(luu):

    os.remove(luu)

LIVE = Fore.GREEN + 'LIVE'

DIE  = Fore.RED   + 'DIE'

def check_proxy(proxy):

    try:

        # Thực hiện kết nối đến trang web bằng cách sử dụng proxy SOCKS5

        socks.set_default_proxy(socks.SOCKS5, proxy.split(':')[0], int(proxy.split(':')[1]))

        socket.socket = socks.socksocket

        response = requests.get('http://httpbin.org/ip', timeout=5)

        if response.ok:

            print(f'{LIVE} {proxy}')

            open(luu, 'a').write(proxy + '\n')

    except:

        print(f'{DIE} {proxy}')

if __name__ == '__main__':

    # Lấy thông tin proxy từ https://free-proxy-list.net/

    url1 = ' https://www.freeproxy.world/?type=socks5&anonymity=&country=&speed=&port=&page=1'

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

# Mở tệp test.txt để đọc và ghi

with open("test.txt", "r+") as file:

    # Đọc nội dung của tệp

    content = file.readlines()

    # Tạo danh sách mới để lưu trữ các dòng đã được chỉnh sửa

    new_lines = []

    # Lặp qua danh sách các dòng

    for line in content:

        # Sử dụng strip() để loại bỏ khoảng trắng dư thừa và ký tự xuống dòng cuối cùng

        line = line.strip()

        # Nếu dòng hiện tại rỗng, tiếp tục vòng lặp

        if not line:

            continue

        # Nếu dòng chứa số port, hãy thêm địa chỉ IP vào dòng trước đó

        if line.isdigit():

            new_lines[-1] += ":" + line

        else:

            # Thêm dòng mới vào danh sách dòng đã được chỉnh sửa

            new_lines.append(line)

    # Đưa con trỏ về đầu tệp

    file.seek(0)

    # Xóa nội dung cũ của tệp

    file.truncate()

    # Ghi lại các dòng đã được chỉnh sửa vào tệp

    file.write("\n".join(new_lines))

# Mở tệp test.txt để đọc và ghi

with open("test.txt", "r+") as file:

    # Đọc nội dung của tệp

    content = file.readlines()

    # Tạo danh sách mới để lưu trữ các dòng đã được chỉnh sửa

    new_lines = []

    # Lặp qua danh sách các dòng

    for line in content:

        # Sử dụng strip() để loại bỏ khoảng trắng dư thừa và ký tự xuống dòng cuối cùng

        line = line.strip()

        # Nếu dòng hiện tại rỗng, tiếp tục vòng lặp

        if not line:

            continue

        # Nếu dòng chứa số port, hãy tách nó ra khỏi địa chỉ IP ở dòng trước đó

        if line.startswith("::"):

            ip_line = new_lines[-1]

            port = line.replace("::", "")

            new_lines[-1] = ip_line + ":" + port

        else:

            # Thêm dòng mới vào danh sách dòng đã được chỉnh sửa

            new_lines.append(line)

    # Đưa con trỏ về đầu tệp

    file.seek(0)

    # Xóa nội dung cũ của tệp

    file.truncate()

    # Ghi lại các dòng đã được chỉnh sửa vào tệp

    file.write("\n".join(new_lines))

    # Lấy thông tin proxy từ https://hidemy.name/en/proxy-list/

    url2 = 'https://www.socks-proxy.net/'

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

                file.write(f"{ip}:{port}\n")

        print("Đã lưu thông tin proxy từ hidemy.name/en/proxy-list/ vào tệp", file_path)

    url2 = 'http://pubproxy.com/api/proxy?limit=20&format=json&type=http'

    response = requests.get(url2)

    json_data = json.loads(response.text)

    for data in json_data['data']:

        ip = data['ip']

        port = data['port']

        # Ghi thông tin proxy vào tệp

        with open(file_path, 'a') as file:

            file.write(f'{ip}:{port}\n')

    print("Đã lưu thông tin proxy từ pubproxy.com/api/proxy vào tệp", file_path)

    with open(file_path) as f:

        all_proxies = f.read().split('\n')

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:

        executor.map(check_proxy, all_proxies)

