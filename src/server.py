import socket


def read_html_template():
    """
    Keeping this as a seperate file so I can easily change html whenever I want
    """
    with open("index.html", "r") as f:
        return f.read()


HTML = read_html_template()


class HttpSocketWrapper:
    def __init__(self, socket: socket.socket) -> None:
        self.s = socket

    def send_html_200(self):
        """`HTTP/1.1 200 OK` + html content"""
        self.s.send("HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n" + HTML)

    def send_404(self):
        """`HTTP/1.1 404 Not Found`"""
        self.s.send("HTTP/1.1 404 Not Found\r\n")

    def redirect_home(self):
        """`HTTP/1.1 303 See Other\r\nLocation: /`
        Seems to be problematic with safari"""
        self.s.send("HTTP/1.1 303 See Other\r\nLocation: /\r\n")


class HttpSocket:
    def __init__(self) -> None:
        host_addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        s = socket.socket()
        self.http_socket = s

        s.settimeout(3)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(host_addr)
        s.listen(1)

        print("[HTTP]: listening on", host_addr)

    def _accept(self):
        try:
            # since it socket.accept() destructures it will cause error
            # with socket.settimeout(5) due to the possibility of no socket operation
            cl, addr = self.http_socket.accept()
        except:
            print("[HTTP]: no requests")
            return None
        print("[HTTP]: client connected from", addr)
        return HttpSocketWrapper(cl)

    def accept(self):
        cl = self._accept()
        if not cl:
            return None

        request = cl.s.recv(1024).decode()
        print("[HTTP_REQUEST]:\n", request + "\n---REQUEST END---")
        return cl, request
