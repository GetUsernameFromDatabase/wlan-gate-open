import network
import time

from server import HttpSocket
from env import SSID, WLAN_PASS, SIGNAL_DURATION
from error_management import ErrorSleep, on_error as on_error_generic
from machine import Pin

GATE_PIN = Pin(15, Pin.OUT)
PICO_LED = Pin("LED", Pin.OUT)

WLAN = network.WLAN(network.STA_IF)
ERROR_SLEEP = ErrorSleep()
S80 = HttpSocket()


def on_error(error: Exception):
    return on_error_generic(error, PICO_LED)


def write_wlan_status(content: str):
    s = "[WLAN]: " + content
    print(s)
    with open("wlan_status.txt", "w") as f:
        f.write(s)


def connect_to_wlan():
    WLAN.active(True)
    WLAN.connect(SSID, WLAN_PASS)

    max_wait = 10
    while max_wait > 0:
        status = WLAN.status()
        if status < 0 or status >= 3:
            break
        max_wait -= 1

        write_wlan_status("waiting for connection...")
        time.sleep(1)

    if status != 3:
        raise RuntimeError("[WLAN]: network connection failed, status: " + str(status))

    ip_data = WLAN.ifconfig()
    write_wlan_status("connected\n" + " - ip = " + ip_data[0])


def gate_toggle():
    def relay_on():
        PICO_LED.on()
        print(f"[GATE]: switching relay pins on")

        GATE_PIN.on()

    def relay_off():
        time.sleep_ms(SIGNAL_DURATION)
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

    # Listen for connections
    while True:
        try:
            accept_result = S80.accept()
            if not accept_result:
                # no requests found
                # sometimes pico gets disconnected from the Wi-FI but this does not
                #   disrupt listening to the socket
                # ensuring that pico is connected to WLAN
                if not WLAN.isconnected():
                    print("[WLAN]: no network connection, retrying")
                    connect_to_wlan()
                continue

            cl, request = accept_result
            # easier to get the address
            before_http = request.split("HTTP", 1)[0].strip()

            if before_http.startswith("POST"):
                # currently will not check request body for `gate=toggle-gate`
                # as this is the only expected behavior for POST
                gate_toggle()
                cl.redirect_home()
            elif before_http.endswith("/favicon.ico"):
                cl.send_404()
            else:
                cl.send_html_200()
                # Will reset the index since it was successfully able to get here
                ERROR_SLEEP.reset()

            cl.s.close()

        except OSError as e:
            cl.s.close()
            on_error_generic(e, None, "socket_error.log")


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
