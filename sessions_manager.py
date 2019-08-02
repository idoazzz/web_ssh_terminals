import json
import logging
from logging import getLogger, DEBUG

from pexpect import spawn, pxssh, EOF
from pexpect import TIMEOUT as READING_TIMEOUT_EXCEPTION


class SSHSession(object):
    """Represents a ssh session that holds an interactive process.

    Attributes:
        sub_process (spawn): Holds the pxssh sub process.
        session_name (str): Session name.
        logger (Logger): Session logger.
    """
    TIMEOUT = 0.001  # Seconds, reading interval.
    CHUNK_SIZE = 4096  # Bytes.

    def __init__(self, session_name, hostname, username,
                 password, save_output=True):

        self.sub_process = None
        self.session_name = session_name

        self.hostname = hostname
        self.username = username
        self.password = password

        logging.basicConfig()
        self.logger = getLogger(session_name)
        self.logger.setLevel(DEBUG)

        self.save_output = save_output
        self.output = ""

    def start(self):
        """Spawning the ssh session sub process."""
        self.logger.debug("Spawning ssh session...")

        try:
            self.sub_process = pxssh.pxssh(encoding="utf8")
            self.sub_process.login(self.hostname, self.username, self.password,
                                   auto_prompt_reset=False)

        except pxssh.ExceptionPxssh as e:
            self.logger.critical("Failed on login.")
            self.logger.exception(e)

    def exit(self):
        """Terminate the session."""
        self.logger.debug("Exiting %s ssh session", self.session_name)
        self.sub_process.logout()

    def send_input(self, data):
        """Send single command input to the ssh session.

        Args:
            data (str): Terminal command.
        """
        self.logger.debug("Sending %s", data)
        self.sub_process.sendline(data)

    def send_inputs(self, *args):
        """Send several inputs to the session input."""
        for arg in args:
            self.send_input(arg)

    def read_output(self, size=CHUNK_SIZE):
        """Read an output from the remote shell stdout.

        We read each time up to CHUNK_SIZE bytes with a timeout of TIMEOUT.
        We always stop to read after TIMEOUT and return the result.

        Args:
            size (int): The size of reading buffer.
        """
        result = ""
        try:
            while True:
                current = self.sub_process.read_nonblocking(size, self.TIMEOUT)
                result += current

        except READING_TIMEOUT_EXCEPTION:
            pass

        except EOF:
            pass

        if result is not "" and self.save_output:
            self.output += result

        return result if result is not "" else None

    def __str__(self):
        return f"Session: {self.session_name} Is Active: {self.active}."


class SessionsManager:
    """Sessions manager that holds all the interactive shells."""

    def __init__(self):
        self._sessions = {}

    def load_session(self, session_name, hostname, username, password):
        """Load and start a specific shell session."""
        self[session_name] = SSHSession(session_name, hostname, username,
                                        password)

        return self[session_name]

    @property
    def sessions(self):
        """Return json dump with sessions state."""
        sessions = {key: str(value) for key, value in self._sessions.items()}
        return json.dumps(sessions)

    def exists(self, session_name):
        """Check if the session exists."""
        return session_name in self._sessions.keys()

    def start(self, session_name):
        """Start a specific session."""
        if self.exists(session_name):
            self[session_name].start()

    def terminate_session(self, session_name):
        """Terminate a specific session."""
        if self.exists(session_name):
            self[session_name].exit()
            del self[session_name]

    def broadcast(self, *args):
        """Send commands to all the active sessions.

        Args:
            args (list): Commands for execute.
        """
        for _session in self:
            _session.send_inputs(*args)

    def __getitem__(self, item):
        return self._sessions[item]

    def __setitem__(self, key, value):
        self._sessions[key] = value

    def __delitem__(self, key):
        del self._sessions[key]

    def __iter__(self):
        return iter(self._sessions.values())

    def __str__(self):
        return str(self._sessions)
