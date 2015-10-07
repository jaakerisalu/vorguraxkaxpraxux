from http.server import HTTPServer, BaseHTTPRequestHandler, urllib
import cgitb
import json
import random
import socket
from socketserver import ThreadingMixIn
import sys
from urllib.error import URLError
from urllib.parse import urlparse, parse_qs
import urllib.request as urlr
import time

cgitb.enable()

CURRENT_SERVER_STATUS = {'slaves':[]}


class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_POST(s):
        s.send_response(200)
        s.end_headers()

        parser = urlparse(s.path)
        if parser.path == "/startcrack":
            length = int(s.headers['Content-Length'])
            post_data = urllib.parse.parse_qs(s.rfile.read(length).decode('utf-8'))
            print("CHECK OUT MY CRACK YO", post_data)

    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        print('GET')

        parser = urlparse(s.path)

        is_boss = False
        md5 = ""

        print(parser)

        if parser.path == "/crack":
            qs = parse_qs(parser.query)
            print('MD5', qs['md5'])
            make_resource_request(noask=["http://127.0.0.1:%s" % CURRENT_SERVER_STATUS['port']], ttl=5, id='yolocrack')
            # CURRENT_SERVER_STATUS['waiting'] = True
            time.sleep(5)
            # CURRENT_SERVER_STATUS['waiting'] = False
            init_cracker(qs['md5'])

        if parser.path == "/resource":
            qs = parse_qs(parser.query)
            # The server gets a request from themselves once they finish sending out all other requests. Ignore it
            print(parse_qs(parser.query))
            if int(qs['sendport'][0]) == CURRENT_SERVER_STATUS['port'] and socket.gethostbyname(socket.gethostname()) == qs['sendip'][0]:
                return

            ttl = int(qs['ttl'][0]) - 1
            if ttl > 1:
                make_resource_request(noask=["http://" + x.replace("_", ":") for x in qs['noask']], ttl=ttl,
                                      id=qs['id'][0], ip=qs['sendip'][0], port=qs['sendport'][0])

            # MAKE RESPONSE
            if not CURRENT_SERVER_STATUS['waiting']:
                print('I must respond')
                make_ready_response(qs['sendip'][0] + ":" + qs['sendport'][0])

        if parser.path == "/ready":
            qs = parse_qs(parser.query)
            print("I RECIEVED A RESPONCE FROM SLAVE")
            CURRENT_SERVER_STATUS['slaves'].append({
                'ip': "http://" + qs['sendip'][0] + ":" + qs['sendport'][0],
                'resource_amount': qs['available'][0]
            })

            if len(CURRENT_SERVER_STATUS['slaves']) == 3:
                print(CURRENT_SERVER_STATUS['slaves'])

        # if is_boss:
        #     post_test(md5)


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


def make_resource_request(noask=None, ttl=5, id="gregorjaakrannar", ip=None, port=None):
    if not noask:
        noask = []

    # Part 1: Send out the resource requests
    machines = get_machines()

    # If there's a previous noask list, filter out machines we don't want to send to
    # TODO: Add sender IP to noask
    if len(noask):
        machines = [x for x in machines if x not in noask]

    noask_list = "&noask=".join([x.replace("http://", "").replace(":", "_") for x in list(set(machines + noask))])

    """
    Final url template:
    http://11.22.33.44:2345/resource?sendip=55.66.77.88&sendport=6788&ttl=5&id=wqeqwe23&noask=11.22.33.44_345&noask=111.222.333.444_223
    """
    params = "/resource?sendip=" + (socket.gethostbyname(socket.gethostname()) if not ip else ip) \
             + "&sendport=" + (str(CURRENT_SERVER_STATUS['port']) if not ip else port) \
             + "&ttl=" + str(ttl)\
             + "&id=" + str(id)\
             + "&noask=" + noask_list
    print(params)

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


def make_ready_response(target):
    params = "/ready?sendip=" + socket.gethostbyname(socket.gethostname())\
             + "&sendport=" + str(CURRENT_SERVER_STATUS['port'])\
             + "&available=%d" % random.randint(0, 100)
    req = urlr.Request("http://" + target + params)
    print("Trying to request: " + "http://" + target + params)
    try:
        response = urlr.urlopen(req, timeout=1)
        r = response.read()
    except URLError as e:
        print("Success response failed " + str(e.reason))
    except socket.timeout as e:
        print("Socket timed out on success")


def make_assignment(ip, tasks, md5):
    print("POSTIN CRACK ASSIGNMENT")
    url = ip + "/startcrack"
    values = {
        "ip": socket.gethostbyname(socket.gethostname()),
        "port": CURRENT_SERVER_STATUS['port'],
        "md5": md5,
        "ranges": tasks,
        "wildcard": "?",
    }

    data = urllib.parse.urlencode(values)
    binary_data = data.encode('utf-8')
    req = urlr.Request(url, binary_data)
    try:
        print("Req", req)
        response = urlr.urlopen(req)
    except urlr.http.client.HTTPException as e:
        print(e)


def init_cracker(md):
    # make_resource_request()
    # peaks time outima, vastuseid ootama.
    threes = ["?"]
    fours = ["??"]
    char = 32  # start with this char ascii (space)
    while char < 126:
        threes.append(str(chr(char)) + "??")
        fours.append(str(chr(char)) + "???")
        char += 1

    task_count = len(threes) + len(fours)  # Spoiler: 190
    slaves = len(CURRENT_SERVER_STATUS['slaves'])
    each = int(task_count / slaves)
    i = 0
    for slave in CURRENT_SERVER_STATUS['slaves']:
        i += 1
        if i == slaves:
            tasks = threes + fours
        else:
            tasks = threes[:int(each/2)] + fours[:int(each/2)]
            threes = threes[int(each/2):]
            fours = fours[int(each/2):]
        make_assignment(slave['ip'], tasks, md)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass
    # top le kek


def run(port):
    server = ThreadedHTTPServer
    handler = MyHandler
    server_address = ("", port)

    global CURRENT_SERVER_STATUS
    CURRENT_SERVER_STATUS['port'] = port
    CURRENT_SERVER_STATUS['waiting'] = False

    httpd = server(server_address, handler)
    print("I am waiting on port %s" % port)

    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run(int(sys.argv[1]))
    else:
        print('Run with server.py my_port')


