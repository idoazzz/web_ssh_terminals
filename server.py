import os

import yaml
from attrdict import AttrDict
from flask import Flask, jsonify, render_template, request, session
from flask_socketio import SocketIO, join_room, leave_room

from runners import RunnersManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

socket = SocketIO(app,
                  static_url_path='/static',
                  logger=True,
                  engineio_logger=True,
                  async_mode="eventlet")

RUNNERS_CONFIG = "runners_config.yml"


class RunnerManagerBackgroundTask(RunnersManager):
    """Manage runner runner input and output.

    Managing the client runner session with the server means that this class
    initiate a thread that listening for new output in the runner.
    If we found new output, we emitting this output to the client through
    websocket. If the client want to send something to the runner, it's
    passes here also.

    Attributes:
        runners_listeners (dict): Contains threads that listening for new
        output.
    """
    FILTER_RULES = {
        "\\x1b": "\x1B",
        "\n": "<br>",
        "]0;": ""
    }

    def __init__(self):
        super(RunnerManagerBackgroundTask, self).__init__()
        self.runners_listeners = {}

        with open(RUNNERS_CONFIG) as runners_config:
            config = runners_config.read()
            self.config = AttrDict(yaml.load(config))

    @property
    def active_runners(self):
        """Return the active runners."""
        return self._runners

    def restart(self, terminal_id, host, username, password):
        """Restart the runner and the listening thread.

        Args:
            terminal_id (str): Socket and runner identifier.
            host (str): Remote host.
            username (str): Target username.
            password (str): Target password.
        """
        if len(self.active_runners) >= self.config.runners_limit:
            raise IndexError("Cannot add new runner.")

        if not self.exists(terminal_id):
            self.load_runner(terminal_id, self.config.setup_command,
                             host, username, password)
        else:
            self.stop(terminal_id)

        self.start(terminal_id)
        self.runners_listeners[terminal_id] = socket. \
            start_background_task(self.listen_for_output, terminal_id)

        for command in self.config.startup_commands:
            self.send_input(terminal_id, command)

        socket.emit("is_active", True, room=terminal_id)

    def stop(self, terminal_id):
        """Stopping the listening thread and the runner.

        Args:
            terminal_id (str): Socket and runner identifier.
        """
        if self.exists(terminal_id):
            socket.emit("is_active", False, room=terminal_id)
            self.terminate_runner(terminal_id)  # Will end the thread
            self.runners_listeners[terminal_id] = None

    def listen_for_output(self, terminal_id):
        """Listen for new output and emitting to the client.

        Args:
            terminal_id (str): Socket and runner identifier.
        """
        while self.exists(terminal_id):
            output = self[terminal_id].read_output()
            if output is not None:
                output = self.filter_output(output)
                socket.emit('new_output', output, room=terminal_id)
            else:
                socket.sleep(0)

    def send_input(self, terminal_id, command):
        """Sending input to the runner.

        Args:
            terminal_id (str): Socket and runner identifier.
            command (str): Input for the runner.
        """
        if not self.exists(terminal_id):
            return

        self[terminal_id].send_inputs(command)

    def send_runner_history(self, terminal_id):
        """Send the history of the runner to a specific room."""

        if not self.exists(terminal_id):
            return

        terminal_content = self[terminal_id].output
        socket.emit('terminal_history', self.filter_output(terminal_content),
                    room=terminal_id)

    def filter_output(self, output):
        """Filtering the runner output and adjust the output to the client.

        Args:
            output (str): Runner output that need to be filtered.
        """
        for key, value in self.FILTER_RULES.items():
            output = output.replace(key, value)
        return output


runner_manager = RunnerManagerBackgroundTask()


@app.route("/")
def index():
    """Serving the index page."""
    return render_template('index.html')


@app.route("/runner/<runner_id>/active")
def is_active(runner_id):
    """Serving the index page."""
    return jsonify(runner_manager.exists(runner_id))


@app.route("/runners")
def get_runners():
    """Serving the index page."""
    return runner_manager.runners


@socket.on("start_runner")
def start_runner(terminal_id, host, username, password):
    """Starting/Restarting the runner."""
    runner_manager.restart(terminal_id, host, username, password)


@socket.on("stop_runner")
def stop_runner(terminal_id):
    """Stopping the runner."""
    runner_manager.stop(terminal_id)


@socket.on("join_terminal")
def join_terminal(terminal_id):
    """Joining the terminal room."""
    join_room(terminal_id)
    runner_manager.send_runner_history(terminal_id)


@socket.on("leave_terminal")
def leave_terminal(terminal_id):
    """Leaving the terminal room."""
    leave_room(terminal_id)


@socket.on('new_input')
def handle_message(data):
    """Sending new input to the runner."""
    runner_manager.send_input(data["terminal_id"], data["command"])


@socket.on('disconnect')
def disconnect():
    pass


@socket.on('connect')
def connection():
    pass


if __name__ == '__main__':
    socket.run(app, host='127.0.0.1', port=8000, debug=True)
