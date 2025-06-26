import network
import socket
import time

from env import SSID, WLAN_PASS
from machine import Pin

GATE_PIN = Pin(15, Pin.OUT)
PICO_LED = Pin("LED", Pin.OUT)


def on_error(error: Exception):
    # This is to notify that something went wrong
    PICO_LED.on()

    with open("error.log", "w") as f:
        f.write(str(error))


def read_html_template():
    """
    Keeping this as a seperate file so I can easily change html whenever I want
    """
    with open("index.html", "r") as f:
        return f.read()


def write_wlan_status(content: str):
    s = "WLAN_STATUS: " + content
    print(s)
    with open("wlan_status.txt", "w") as f:
        f.write(s)


def connect_to_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, WLAN_PASS)

    max_wait = 10
    while max_wait > 0:
        status = wlan.status()
        if status < 0 or status >= 3:
            break
        max_wait -= 1

        write_wlan_status("waiting for connection...")
        time.sleep(1)

    if status != 3:
        raise RuntimeError("network connection failed, status: " + str(status))

    ip_data = wlan.ifconfig()
    write_wlan_status("connected\n" + "ip = " + ip_data[0])


def setup_http_server():
    host_addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(host_addr)
    s.listen(1)
    print("listening on", host_addr)
    return s


def gate_toggle():
    def relay_on():
        PICO_LED.on()
        print(f"-/\\ switching relay pins on")

        GATE_PIN.on()

    def relay_off():
        time.sleep_ms(1500)  # more reliable when it blocks other things
        PICO_LED.off()
        print(f"-\\/ switching relay pins off")

        GATE_PIN.off()

    relay_on()
    relay_off()


def signal_start():
    """
    This lets me know that the script started
    """
    for _i in range(5):
        PICO_LED.on()
        time.sleep_ms(100)
        PICO_LED.off()
        time.sleep_ms(100)


def main():
    signal_start()
    connect_to_wlan()

    html = read_html_template()
    s = setup_http_server()

    # Listen for connections
    while True:
        try:
            cl, addr = s.accept()
            print("client connected from", addr)
            request = cl.recv(1024).decode()
            print("RAW_REQUEST:\n", request, "\n")

            # this makes sure that gate=toggle-gate will be found only on request address
            #   and not (for example) in the Referer section
            before_http = str(request).split("HTTP", 1)[0].strip()

            if before_http.startswith("POST"):
                # currently will not check request body for `gate=toggle-gate`
                # as this is the only expected behavior for POST
                gate_toggle()
                cl.send("HTTP/1.1 303 See Other\r\nLocation: /")
            elif before_http.endswith("/favicon.ico"):
                cl.send("HTTP/1.1 404 Not Found")
            else:
                cl.send("HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n" + html)

            cl.close()

        except OSError as e:
            cl.close()
            print("connection closed")


if __name__ == "__main__":
    try:
        # uasyncio.run(main())
        main()
    except Exception as e:
        on_error(e)
        # so that it would quit and display print to system (debug)
        raise e
