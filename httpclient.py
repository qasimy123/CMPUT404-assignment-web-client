#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# with Contributions from Qasim Khawaja
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it
import urllib.parse
import re
import socket
import sys
EOL = "\r\n"
# you may use urllib to encode data appropriately


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        header = self.get_headers(data)
        # print("NUM",header.split(" ")[1])
        return int(header.split(" ")[1])

    def get_headers(self, data):
        return data.split(f"{EOL}{EOL}")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = self.parse_url(url)

        req = f"GET {path} HTTP/1.1{EOL}Host: {host}{EOL}Connection: close{EOL}{EOL}"
        self.connect(host, port)
        self.sendall(req)
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def parse_url(self, url):
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path
        protocol = parsed_url.scheme
        # print(host, port, path, protocol)
        if not port:
            if protocol == "https":
                port = 443
            else:
                port = 80
        if not path:
            path = "/"
        return host, port, path

    def POST(self, url, args=None):
        host, port, path = self.parse_url(url)
        req = f"POST {path} HTTP/1.1{EOL}Host: {host}{EOL}Connection: close{EOL}Content-Type: application/x-www-form-urlencoded{EOL}"
        if args:
            body = urllib.parse.urlencode(args)
            req += f"Content-Length: {len(body)}{EOL}{EOL}{body}"
        else:
            req += f"Content-Length: 0{EOL}{EOL}"
        self.connect(host, port)
        self.sendall(req)
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
