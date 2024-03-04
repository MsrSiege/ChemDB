# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from sys import exc_info, excepthook
from threading import Thread


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-21    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class ReturnThread(Thread):
    """Custom Thread that returns the value of the threaded function.\n
    Source 1: https://github.com/cocuni80/thread_decorator\n
    Source 2: https://alexandra-zaharia.github.io/posts/how-to-return-a-result-from-a-python-thread/"""

    result = None
    error = None

    def run(self, *args, **kwargs):
        """Runs the target function and sets the result or the error, if any."""
        try:
            if self._target:
                self.result = self._target(*self._args, **self._kwargs)
        except Exception as Error:
            self.error = Error
        finally:
            # Avoid a refcycle if the thread is running a function with an argument that points to the thread.
            del self._target, self._args, self._kwargs

    def await_result(self):
        """Waits for the thread to finish and returns the result."""
        self.join()
        return self.result

    def await_error(self):
        """Waits for the thread to finish and returns an error, if any."""
        self.join()
        return self.error


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-03-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def RerouteThreadingExcepthook():
    """Installs a custom excepthook for threading.Thread class which reroutes all exceptions to the main threads' excepthook
    and thereby to the main logging module.\n
    Source: https://www.lesinskis.com/python-excepthook-logging.html"""

    thread_init = Thread.__init__

    def reroute_init(self, *args, **kwargs):
        thread_init(self, *args, **kwargs)
        thread_run = self.run

        def reroute_run(*args, **kwargs):
            try:
                thread_run(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:  # noqa: E722
                excepthook(*exc_info())

        self.run = reroute_run

    Thread.__init__ = reroute_init
