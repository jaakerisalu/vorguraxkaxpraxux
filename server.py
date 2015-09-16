from http.server import HTTPServer, BaseHTTPRequestHandler
import cgitb;
import sys

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

def init_cracker(port):
    print('cracking')
    req = urlr.Request('http://127.0.0.1:%s/test' % port)
    print(req)
    with urlr.urlopen(req) as response:
        print('trying to read')
        lol = response.read()
        print(lol)


def run(port, target_port, is_first=False):
    server = HTTPServer
    handler = MyHandler
    server_address = ("", port)

    httpd = server(server_address, handler)

    if not is_first:
        init_cracker(target_port)

    print("My port is %s" % port)
    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) == 4:
        run(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    elif len(sys.argv) == 3:
        run(int(sys.argv[1]), int(sys.argv[2]))
    else:
        print('Run with server.py my_port target_port is_first')

