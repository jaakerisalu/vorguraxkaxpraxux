from http.server import urllib
import json
import random
import socket
from urllib.error import URLError
import urllib.request as urlr
import globals


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


def make_stop_request(ip, port):
    dont_ask_url = "http://" + ip + ":" + port

    for slave in globals.CURRENT_SERVER_STATUS['slaves']:
        if slave['ip'] != dont_ask_url:

            print("Stopping", slave['ip'])

            req = urlr.Request(slave['ip'] + "/stopcrack")
            try:
                response = urlr.urlopen(req, timeout=1)
                r = response.read()
            except URLError as e:
                print("Something is fukt, more specifically: " + str(e.reason))
            except socket.timeout as e:
                print("Socket timed out, moving on")


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
             + "&sendport=" + (str(globals.CURRENT_SERVER_STATUS['port']) if not ip else port) \
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
             + "&sendport=" + str(globals.CURRENT_SERVER_STATUS['port'])\
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


def make_result_found_request(my_ip, my_port, ip, port, md5, result, resultstring):

    url = "http://" + ip + ":" + port + "/result"

    values = {
        "ip": my_ip,
        "port": my_port,
        "md5": md5,
        "result": result,
        "resultstring": resultstring
    }

    print("STOPPING", url)
    data = urllib.parse.urlencode(values)
    binary_data = data.encode('utf-8')
    req = urlr.Request(url, binary_data)
    try:
        print("Req", req)
        response = urlr.urlopen(req, timeout=1)
    except urlr.http.client.HTTPException as e:
        print(e)


def make_assignment(ip, tasks, md5):
    wildcard = "?"

    print("POSTIN CRACK ASSIGNMENT")
    url = ip + "/startcrack"
    values = {
        "ip": socket.gethostbyname(socket.gethostname()),
        "port": globals.CURRENT_SERVER_STATUS['port'],
        "md5": md5,
        "ranges": tasks,
        "wildcard": wildcard,
    }

    data = urllib.parse.urlencode(values)
    binary_data = data.encode('utf-8')
    req = urlr.Request(url, binary_data)
    try:
        print("Req", req)
        response = urlr.urlopen(req, timeout=1)
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
    slaves = len(globals.CURRENT_SERVER_STATUS['slaves'])
    each = int(task_count / slaves)
    i = 0
    for slave in globals.CURRENT_SERVER_STATUS['slaves']:
        i += 1
        if i == slaves:
            tasks = threes + fours
        else:
            tasks = threes[:int(each/2)] + fours[:int(each/2)]
            threes = threes[int(each/2):]
            fours = fours[int(each/2):]
        make_assignment(slave['ip'], tasks, md)

