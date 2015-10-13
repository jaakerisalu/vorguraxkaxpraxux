from http.server import HTTPServer, BaseHTTPRequestHandler, urllib
import cgitb
from socketserver import ThreadingMixIn
import sys
from urllib.parse import urlparse, parse_qs
import time
import ast
from actions import *
from md5crack import Md5Cracker
import globals

cgitb.enable()


class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "json")
        s.end_headers()

    def do_POST(s):
        s.send_response(200)
        s.end_headers()

        parser = urlparse(s.path)

        length = int(s.headers['Content-Length'])
        post_data = urllib.parse.parse_qs(s.rfile.read(length).decode('utf-8'))

        print("POST RECEIVED ", parser.path)

        if parser.path == "/checkmd5":
            print("CHECK OUT MY CRACK YO", post_data)

            globals.CURRENT_SERVER_STATUS['isfound'] = False

            template_list = list(ast.literal_eval(post_data['ranges'][0]))

            md5 = str(post_data['md5'][0])
            wildcard = str(post_data['wildcard'][0])

            cracker = Md5Cracker()

            for template in template_list:
                if globals.CURRENT_SERVER_STATUS['isfound'] is False:

                    if len(template) > 2 and template.strip(wildcard) == '':
                        continue

                    res = cracker.start(md5, template, wildcard)

                    if res is not None:
                        make_result_found_request(socket.gethostbyname(socket.gethostname()), globals.CURRENT_SERVER_STATUS['port'],
                                              post_data['ip'][0], post_data['port'][0], md5, 0, res)
                        break

            print("Cracking stopped")

        if parser.path == "/answermd5":
            make_stop_request(post_data['ip'][0], post_data['port'][0])
            #THIS IS NOT WORKING ATM
            s.wfile.write(bytes("<p>Slave at %s:%s found solution - %s" % (post_data['ip'][0], post_data['port'][0], post_data['resultstring'][0]), 'UTF-8'))
            print("RESULT:", post_data['resultstring'][0])

        if parser.path == "/resourcereply":
            print("I RECIEVED A RESPONCE FROM SLAVE")
            globals.CURRENT_SERVER_STATUS['slaves'].append({
                'ip': "http://" + post_data['ip'][0] + ":" + post_data['port'][0],
                'resource_amount': post_data['resource'][0]
            })

            if len(globals.CURRENT_SERVER_STATUS['slaves']) == 3:
                print(globals.CURRENT_SERVER_STATUS['slaves'])

    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        print('GET')

        parser = urlparse(s.path)
        s.wfile.write(bytes("<html><head><title>P2P MD5 Cracking network</title></head><p>Accessed path %s on server 127.0.0.1:%s</p></html>" % (s.path, globals.CURRENT_SERVER_STATUS['port']), 'UTF-8'))
        print(parser)

        if parser.path == "/crack":
            s.wfile.write(bytes("<html><p>Initiating slave master, gathering slaves ...</p></html>", 'UTF-8'))
            qs = parse_qs(parser.query)
            print('MD5', qs['md5'])
            make_resource_request(noask=["http://127.0.0.1:%s" % globals.CURRENT_SERVER_STATUS['port']], ttl=5, id='yolocrack')
            # CURRENT_SERVER_STATUS['waiting'] = True
            time.sleep(5)
            # CURRENT_SERVER_STATUS['waiting'] = False
            slaveindex = 0
            for slave in globals.CURRENT_SERVER_STATUS['slaves']:
                s.wfile.write(bytes("Slave %s - %s<br>" % (slaveindex, slave['ip']), 'UTF-8'))
                slaveindex += 1
            init_cracker(qs['md5'][0])
            s.wfile.write(bytes("<p>Initiating cracking on hash - %s</p>" % qs['md5'][0], 'UTF-8'))

        if parser.path == "/stopcrack":
            globals.CURRENT_SERVER_STATUS['isfound'] = True
            print("stopcrack", globals.CURRENT_SERVER_STATUS['isfound'])

        if parser.path == "/resource":
            qs = parse_qs(parser.query)
            # The server gets a request from themselves once they finish sending out all other requests. Ignore it
            print(parse_qs(parser.query))
            if int(qs['sendport'][0]) == globals.CURRENT_SERVER_STATUS['port'] and socket.gethostbyname(socket.gethostname()) == qs['sendip'][0]:
                return

            ttl = int(qs['ttl'][0]) - 1
            if ttl > 1:
                make_resource_request(noask=["http://" + x.replace("_", ":") for x in qs['noask']], ttl=ttl,
                                      id=qs['id'][0], ip=qs['sendip'][0], port=qs['sendport'][0])

            # MAKE RESPONSE
            if not globals.CURRENT_SERVER_STATUS['waiting']:
                print('I must respond')
                make_ready_response(qs['sendip'][0] + ":" + qs['sendport'][0])


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass
    # top le kek


def run(port):
    server = ThreadedHTTPServer
    handler = MyHandler
    server_address = ("", port)

    globals.init()

    globals.CURRENT_SERVER_STATUS['port'] = port
    globals.CURRENT_SERVER_STATUS['waiting'] = False

    httpd = server(server_address, handler)
    print("I am waiting on port %s" % port)

    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run(int(sys.argv[1]))
    else:
        print('Run with server.py my_port')




