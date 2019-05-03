import json
import logging
from logging import getLogger, DEBUG

from pexpect import spawn, pxssh, EOF
from pexpect import TIMEOUT as READING_TIMEOUT_EXCEPTION


class RemoteRunner(object):
    """Represents a generic runner that holds an interactive process.

    Runner is a process that has a job and can be interactive with
    user commander. User can insert input interactively to the process and
    also read the output of the process, interactively.
    For example, Shell can be a runner, it's an infinite process that can
    getting input and return output while it's running.

    Attributes:
        sub_process (spawn): Holds the pxssh sub process.
        runner_name (str): Runner name.
        logger (Logger): Runner logger.
    """
    TIMEOUT = 0.001  # Seconds, reading interval.
    CHUNK_SIZE = 4096  # Bytes.

    def __init__(self, runner_name, hostname, username,
                 password, save_output=True):

        self.sub_process = None
        self.runner_name = runner_name

        self.hostname = hostname
        self.username = username
        self.password = password

        logging.basicConfig()
        self.logger = getLogger(runner_name)
        self.logger.setLevel(DEBUG)

        self.save_output = save_output
        self.output = ""

    def start(self):
        """Spawning the remote runner sub process."""
        self.logger.debug("Spawning remote runner...")
        try:

            self.sub_process = pxssh.pxssh()
            self.sub_process.login(self.hostname, self.username, self.password,
                                   auto_prompt_reset=False)

        except pxssh.ExceptionPxssh as e:
            self.logger.critical("Failed on login.")
            self.logger.exception(e)

    def exit(self):
        """Terminate the runner."""
        self.logger.debug("Exiting %s runner", self.runner_name)
        self.sub_process.logout()

    def send_input(self, data):
        """Send single command input to the runner.

        Args:
            data (str): Terminal command.
        """
        self.logger.debug("Sending %s", data)
        self.sub_process.sendline(data)

    def send_inputs(self, *args):
        """Send several inputs to the runner input."""
        for arg in args:
            self.send_input(arg)

    def read_output(self, size=CHUNK_SIZE):
        """Read an output from the runner.

        We read each time up to CHUNK_SIZE bytes with a timeout of TIMEOUT.
        We always stop to read after TIMEOUT and return the result.

        Args:
            size (int): The size of reading buffer.
        """
        result = b""
        try:
            while True:
                current = self.sub_process.read_nonblocking(size, self.TIMEOUT)
                result += current

        except READING_TIMEOUT_EXCEPTION:
            pass

        except EOF:
            pass

        result = result.decode("unicode_escape")

        if result is not "" and self.save_output:
            self.output += result

        return result if result is not "" else None

    def __str__(self):
        return f"Runner: {self.runner_name} Is Active: {self.active}."


class RunnersManager:
    """Runners manager that holds all the interactive shells."""

    def __init__(self):
        self._runners = {}

    def load_runner(self, runner_name, hostname, username, password):
        """Load and start a specific shell runner."""
        self[runner_name] = RemoteRunner(runner_name, hostname, username,
                                         password)

        return self[runner_name]

    @property
    def runners(self):
        """Return json dump with runners state."""
        runners = {key: str(value) for key, value in self._runners.items()}
        return json.dumps(runners)

    def exists(self, runner_name):
        """Check if the runner exists."""
        return runner_name in self._runners.keys()

    def start(self, runner_name):
        """Start a specific runner."""
        if self.exists(runner_name):
            self[runner_name].start()

    def terminate_runner(self, runner_name):
        """Terminate a specific runner."""
        if self.exists(runner_name):
            self[runner_name].exit()
            del self[runner_name]

    def broadcast(self, *args):
        """Send commands to all the active runners.

        Args:
            args (list): Commands for execute.
        """
        for _runner in self:
            _runner.send_inputs(*args)

    def __getitem__(self, item):
        return self._runners[item]

    def __setitem__(self, key, value):
        self._runners[key] = value

    def __delitem__(self, key):
        del self._runners[key]

    def __iter__(self):
        return iter(self._runners.values())

    def __str__(self):
        return str(self._runners)
