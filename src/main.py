import network
import socket
import time

from env import SSID, WLAN_PASS
from error_management import ErrorSleep, on_error as on_error_generic
from machine import Pin

GATE_PIN = Pin(15, Pin.OUT)
PICO_LED = Pin("LED", Pin.OUT)

ERROR_SLEEP = ErrorSleep()


def on_error(error: Exception):
    return on_error_generic(error, PICO_LED)


def read_html_template():
    """
    Keeping this as a seperate file so I can easily change html whenever I want
    """
    with open("index.html", "r") as f:
        return f.read()


def write_wlan_status(content: str):
    s = "[WLAN_STATUS]: " + content
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
    write_wlan_status("connected\n" + " - ip = " + ip_data[0])


def setup_http_server():
    host_addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(host_addr)
    s.listen(1)

    print("[HTTP]: listening on", host_addr)
    return s


def gate_toggle():
    def relay_on():
        PICO_LED.on()
        print(f"[GATE]: switching relay pins on")

        GATE_PIN.on()

    def relay_off():
        time.sleep_ms(1500)  # more reliable when it blocks other things
        PICO_LED.off()
        print(f"[GATE]: switching relay pins off")

        GATE_PIN.off()

    relay_on()
    relay_off()


def flash_led(count=5, interval=100):
    """Flashes pico led

    Args:
        count (int, optional): How many times to flash. Defaults to 5.
        interval (int, optional): how long led stays on and off, unit is in ms. Defaults to 100.
    """
    for _i in range(count):
        PICO_LED.on()
        time.sleep_ms(interval)
        PICO_LED.off()
        time.sleep_ms(interval)


def main():
    flash_led()
    connect_to_wlan()

    html = read_html_template()
    s = setup_http_server()

    # Listen for connections
    while True:
        try:
            cl, addr = s.accept()
            print("[HTTP]: client connected from", addr)
            request = cl.recv(1024).decode()
            print("[HTTP_REQUEST]:\n", request + "\n---REQUEST END---")

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
                # Will reset the index since it was successfully able to get here
                ERROR_SLEEP.reset()

            cl.close()

        except OSError as e:
            cl.close()
            raise e


if __name__ == "__main__":
    while True:
        try:
            # uasyncio.run(main())
            main()
        except Exception as e:
            # on error will turn the led on but there is no need to turn it off
            #   since main flashes led anyway at the start
            on_error(e)
            ERROR_SLEEP.sleep()
