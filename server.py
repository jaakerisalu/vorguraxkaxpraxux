from http.server import HTTPServer, BaseHTTPRequestHandler
import cgitb;
import json
import socket
import sys
from urllib.error import URLError

cgitb.enable()  ## This line enables CGI error reporting
import urllib.request as urlr

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
        s.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", 'UTF-8'))
        s.wfile.write(bytes("<body><p>This is a test.</p>", 'UTF-8'))
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        s.wfile.write(bytes("<p>You accessed path: %s</p>" % s.path, 'UTF-8'))
        s.wfile.write(bytes("</body></html>", 'UTF-8'))


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


def init_cracker():
    print('Initiating')
    machines = get_machines()
    print("machines: " + str(machines))

    for machine in machines:
        print("Trying to approach machine: " + machine)
        req = urlr.Request(machine)
        try:
            response = urlr.urlopen(req, timeout=1)
            r = response.read()
            print(r)
        except URLError as e:
            print("Something is fukt, more specifically: " + str(e.reason))
        except socket.timeout as e:
            print("Socket timed out, moving on")



def run(port, is_first=False):
    server = HTTPServer
    handler = MyHandler
    server_address = ("", port)

    httpd = server(server_address, handler)

    if not is_first:  # This is for testing and will eventually be deprecated
        init_cracker()

    print("My port is %s" % port)
    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        run(int(sys.argv[1]), sys.argv[2])
    elif len(sys.argv) == 2:
        run(int(sys.argv[1]))
    else:
        print('Run with server.py my_port target_port is_first')

