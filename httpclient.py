#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body="", raw_data=b""):
        self.code = code
        self.body = body
        self.header = ""

        if raw_data:
            self.parse_data(raw_data)

    def __repr__(self):
        return self.body

    def parse_data(self, raw_data):
        header, body = raw_data.split(b"\r\n\r\n", 1)

        # If encoding is not specified, it'll assume it's ISO-8859-1
        encoding = "utf-8" if b"utf-8" in header else "ISO-8859-1"

        self.header = header.decode(encoding)
        self.body = body.decode(encoding)
        self.code = int(self.header[9:12])  # "HTTP/1.1 XXX"


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.url = urllib.parse.urlparse(host)

        try:
            self.socket = socket.create_connection((self.url.hostname, self.url.port or 80))
        except ConnectionError:
            print("Error connecting to host.")
            sys.exit(-1)

        return None

    def get_code(self, data):
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        self.socket.shutdown(socket.SHUT_WR)

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = b''
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer += part
            else:
                done = not part

        self.socket.close()

        return HTTPResponse(raw_data=buffer)

    def format_header(self, method, header_fields=dict()):
        header = "%s %s HTTP/1.1\r\n"\
            "Host: %s\r\n"\
            "Accept: */*\r\n"\
            "User-agent: A2Client\r\n" % (method, self.url.path or '/', self.url.hostname)

        for key, value in header_fields.items():
            header += "%s: %s\r\n" % (key, value)

        return header + "\r\n"

    def GET(self, url, args=None):
        # Here because tests call GET and POST directly...
        self.connect(url, 80)

        payload = self.format_header("GET")

        self.sendall(payload)

        return self.recvall()

    # POST sends a post request to url
    # url url to send request to 
    # args - a dictionary with arguments of the post request.
    def POST(self, url, args=None):
        self.connect(url, 80)

        try:
            encoded_params = urllib.parse.urlencode(args)
        except TypeError:
            encoded_params = ""

        payload = self.format_header(
            "POST",
            header_fields={
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": len(encoded_params)
            })

        print(payload)

        payload += encoded_params

        self.sendall(payload)

        return self.recvall()

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

    client.close()
