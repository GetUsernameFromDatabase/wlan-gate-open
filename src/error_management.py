import time
from machine import Pin

ERROR_LOG_FILE = "error.log"

# move this into a utils file when needed elsewhere as well
# small project so might as well stay here
def class_print(cls: object, printable: object):
    class_name = cls.__class__.__name__
    print(f"[{class_name}]:", printable)


class ErrorSleep:
    """ErrorSleep is used to wait till a new attempt is tried
    at whatever caused an error
    """

    def __init__(self, intervals=[5, 15, 30, 180, 600]):
        """Initializes ErrorSleep

        Args:
            intervals (list, optional): the amount of time to sleep in seconds,
                will be cycled through. Defaults to [5, 15, 30, 180, 600].
        """
        self.intervals = intervals
        self.index = 0

    def get_current_interval(self):
        return self.intervals[self.index]

    def next_interval(self):
        """Sets next interval and returns it"""
        if self.is_last_interval():
            self.reset()
        else:
            self.index += 1

        return self.get_current_interval()

    def reset(self):
        """Resets the interval index"""
        self.index = 0

    def is_last_interval(self):
        return self.index == len(self.intervals) - 1

    def sleep(self):
        """Sleeps for the amount of time to sleep at the current interval
        then increments index by 1
        """
        interval = self.get_current_interval()
        class_print(self, f"sleeping for {interval} seconds")
        time.sleep(self.get_current_interval())
        self.next_interval()


def on_error(error: Exception, indicator_led: Pin):
    """Prints the error and writes it into a file

    Args:
        error (Exception): The Exception to print and log
        indicator_led (Pin): pin to turn on, meant to describe error
    """
    # This is to notify that something went wrong
    indicator_led.on()

    print(str(error))
    with open(ERROR_LOG_FILE, "w") as f:
        f.write(str(error))
