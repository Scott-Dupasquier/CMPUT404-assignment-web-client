#!/usr/bin/env python3
# coding: utf-8
# Copyright 2020 Scott Dupasquier
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
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # The response code is always in position 1 after splitting the data
        return int(data.split()[1])

    def get_headers(self, data):
        return None

    def get_body(self, data):
        body = ""
        index = 0
        data = data.split('\n')

        # '\r' alone marks the end of headers and beginning of the body
        while data[index] != '\r':
            index += 1

        index += 1 # Move past the \r since it shouldn't be returned
        while index < len(data):
            # Concatenate the rest of the strings together and re-insert the
            # new line characters to get the body
            body += data[index] + '\n'
            index += 1
        
        return body
    
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
        # Parse the URL and retrieve the hostname
        url_data = urllib.parse.urlparse(url)
        host = url_data.netloc
        if ':' in host:
            host = host.split(':')[0]
        port = url_data.port

        # Create the payload
        payload = "GET " + url_data.path + " HTTP/1.1\r\nHost: " + url_data.netloc + "\r\nConnection: close\r\n\r\n"

        # Connect to the site
        self.connect(host, port)

        # Send the payload
        self.sendall(payload)

        # Get response back and retrieve code and body
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        
        self.close() # Need to close the socket

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Parse the URL and retrieve the hostname
        url_data = urllib.parse.urlparse(url)
        host = url_data.netloc
        if ':' in host:
            host = host.split(':')[0]
        port = url_data.port

        # Get the content length and form the key-value pairs in html format
        content_len = 0
        pairs = ""
        if args:
            # Should get this result: pairs = "a=aaaaaaaaaaaaa&b=bbbbbbbbbbbbbbbbbbbbbb&c=c&d=012345\r67890\n2321321\n\r"
            for arg in args.keys():
                pairs += arg + "="
                value = args[arg].encode('unicode-escape').decode('unicode-escape')
                pairs += value + "&" # Need & for the next key-value pair

            # Remove the last character since it is &
            pairs = pairs[:-1]
            content_len = len(pairs) # Get content length

        # Create the payload
        payload = "POST " + url_data.path + " HTTP/1.1\r\n" + \
        "Host: " + url_data.netloc + "\r\n" + \
        "Content-Type: application/x-www-form-urlencoded\r\n" + \
        "Content-Length: " + str(content_len) + "\r\n\r\n" + pairs

        # Connect to the site
        self.connect(host, port)

        # Send payload
        self.sendall(payload)

        # Get response back and retrieve the code and data
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            response = self.GET( url, args )
            return response
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
