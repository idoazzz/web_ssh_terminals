import logging
from logging import getLogger, DEBUG

from pexpect import spawn, pxssh, EOF
from pexpect import TIMEOUT as READING_TIMEOUT_EXCEPTION


class Runner(object):
    """Represents a generic runner that holds an interactive process.

    Runner is a process that has a job and can be interactive with
    user commander. User can insert input interactively to the process and
    also read the output of the process, interactively.
    For example, Terminal can be a runner, it's an infinite process that can
    getting input and return output while it's running.

    Attributes:
        sub_process (spawn): Holds the pexpect sub process.
        runner_name (str): Runner name.
        logger (Logger): Runner logger.
    """
    TIMEOUT = 0.001  # Seconds, reading interval.
    CHUNK_SIZE = 4096  # Bytes.

    def __init__(self, runner_name, runner_program):
        self.active = False
        self.sub_process = None
        self.runner_name = runner_name
        self.runner_program = runner_program

        logging.basicConfig()
        self.logger = getLogger(runner_name)
        self.logger.setLevel(DEBUG)

    def start(self):
        """Spawning the runner sub process."""
        self.logger.debug("Spawning %s...", self.runner_program)
        self.sub_process = spawn(self.runner_program)
        self.active = True

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
        result = ""
        try:
            while True:
                current = self.sub_process.read_nonblocking(size, self.TIMEOUT)
                result += str(current)[2:-1]

        except READING_TIMEOUT_EXCEPTION:
            pass

        except EOF:
            pass

        return result if result is not "" else None

    def exit(self):
        """Terminate the runner."""
        self.logger.debug("Exiting %s runner", self.runner_name)
        self.sub_process.terminate()
        self.active = False


class RemoteRunner(Runner):
    """Runner that holds a remote runner for interactive use."""

    def __init__(self, runner_name, runner_program, hostname, username,
                 password):

        super(RemoteRunner, self).__init__(runner_name, runner_program)
        self.hostname = hostname
        self.username = username
        self.password = password

    def start(self):
        """Spawning the remote runner sub process."""
        self.logger.debug("Spawning remote runner...")
        try:

            self.sub_process = pxssh.pxssh()
            self.sub_process.login(self.hostname, self.username, self.password)

            super(RemoteRunner, self).start()

        except pxssh.ExceptionPxssh as e:
            print("Failed on login.")
            print(e)
