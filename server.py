from http.server import HTTPServer, BaseHTTPRequestHandler
import cgitb;
import json
import socket
import sys
from urllib.error import URLError
from urllib.parse import urlparse, parse_qs

cgitb.enable()  ## This line enables CGI error reporting
import urllib.request as urlr

CURRENT_SERVER_PORT = 0

class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(s):
         s.send_response(200)
         s.send_header("Content-type", "text/html")
         s.end_headers()

    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        print('Sain k2tte yo')

        parser = urlparse(s.path)
        # print(parser)


        if parser.path == "/crack":
            qs = parse_qs(parser.query)

            print('MD5', qs['md5'])
            make_resource_request(noask=["http://http://127.0.0.1:9000/"], ttl=5, id='yolocrack')



        if parser.path == "/resource":
            qs = parse_qs(parser.query)
            # The server gets a request from themselves once they finish sending out all other requests. Ignore it
            if int(qs['sendport'][0]) == CURRENT_SERVER_PORT and socket.gethostbyname(socket.gethostname()) == qs['sendip'][0]:
                return

            print(parse_qs(parser.query))
            ttl = int(qs['ttl'][0]) - 1
            if ttl > 1:
                make_resource_request(noask=["http://" + x.replace("_", ":") for x in qs['noask']], ttl=ttl, id=qs['id'][0])

            #MAKE RESPONSE
            s.wfile.write(bytes("<html><head><title>you accessed path %s</title></head>" % s.path, 'UTF-8'))


def get_machines():
    """
    Gets a list of machines from the local machines.txt and from P2Net at http://dijkstra.cs.ttu.ee/~priit/P2Net.txt
    """

    url = "http://dijkstra.cs.ttu.ee/~priit/P2Net.txt"
    local_file = "machines.txt"

    res = []
    req = urlr.Request(url)
    with urlr.urlopen(req) as response:
        res = ["http://" + ":".join(x) for x in json.loads(response.read().decode("utf-8"))]

    loc = []
    with open(local_file, encoding='utf-8') as file:
        loc = ["http://" + ":".join(x) for x in json.loads(file.read())]

    return loc + res

def make_resource_request(noask=None, ttl=5, id="gregorjaakrannar"):
    if not noask:
        noask = []

    # Part 1: Send out the resource requests
    machines = get_machines()

    # If there's a previous noask list, filter out machines we don't want to send to
    # TODO: Add sender IP to noask
    if len(noask):
        machines = [x for x in machines if x not in noask]

    noask_list = "&noask=".join([x.replace("http://", "").replace(":", "_") for x in machines + noask])

    """
    Final url template:
    http://11.22.33.44:2345/resource?sendip=55.66.77.88&sendport=6788&ttl=5&id=wqeqwe23&noask=11.22.33.44_345&noask=111.222.333.444_223
    """
    params = "/resource?sendip=" + socket.gethostbyname(socket.gethostname())\
             + "&sendport=" + str(CURRENT_SERVER_PORT)\
             + "&ttl=" + str(ttl)\
             + "&id=" + str(id)\
             + "&noask=" + noask_list

    for machine in machines:
        req = urlr.Request(machine + params)
        # print(machine + params)
        try:
            response = urlr.urlopen(req, timeout=1)
            r = response.read()
        except URLError as e:
            print("Something is fukt, more specifically: " + str(e.reason))
        except socket.timeout as e:
            print("Socket timed out, moving on")

def init_cracker():
    make_resource_request()
    # peaks time outima, vastuseid ootama.

def run(port):
    server = HTTPServer
    handler = MyHandler
    server_address = ("", port)

    global CURRENT_SERVER_PORT
    CURRENT_SERVER_PORT = port

    httpd = server(server_address, handler)

    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run(int(sys.argv[1]))
    else:
        print('Run with server.py my_port')

