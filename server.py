import os

from flask import Flask, jsonify, render_template, request, session
from flask_socketio import SocketIO, join_room, leave_room

from runners import RunnersManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

socket = SocketIO(app, logger=True, engineio_logger=True)

DEFAULT_RUNNER_PROCESS = "python /home/osboxes/projects/sandbox/example.py"


class RunnerManagerBackgroundTask(RunnersManager):
    """Manage runner runner input and output.

    Managing the client runner session with the server means that this class
    initiate a thread that listening for new output in the runner.
    If we found new output, we emitting this output to the client through
    websocket. If the client want to send something to the runner, it's
    passes here also.

    Attributes:
        emitter_threads (dict): Contains threads that listening for new output.
    """
    FILTER_RULES = {
        "\\r": "",
        "\\n": "<br>",
        "\\x1b": "\x1B"
    }

    def __init__(self):
        super(RunnerManagerBackgroundTask, self).__init__()
        self.emitter_threads = {}
        self.runners_contents = {}

    def restart(self, terminal_id):
        """Restart the runner and the listening thread.

        Args:
            terminal_id (str): Socket and runner identifier.
        """
        if not self.exists(terminal_id):
            self.load_runner(terminal_id, DEFAULT_RUNNER_PROCESS)

        if self.is_active(terminal_id):
            self.stop(terminal_id)

        self.start(terminal_id)
        self.emitter_threads[terminal_id] = socket. \
            start_background_task(self.listen_for_output, terminal_id)
        self.runners_contents[terminal_id] = ""

    def stop(self, terminal_id):
        """Stopping the listening thread and the runner.

        Args:
            terminal_id (str): Socket and runner identifier.
        """
        if self.is_active(terminal_id):
            self.terminate_runner(terminal_id)  # Will end the thread
            self.emitter_threads[terminal_id] = None
            self.runners_contents[terminal_id] = None

    def listen_for_output(self, terminal_id):
        """Listen for new output and emitting to the client.

        Args:
            terminal_id (str): Socket and runner identifier.
        """
        while self.is_active(terminal_id):
            output = self[terminal_id].read_output()
            if output is not None:
                output = self.filter_output(output)
                self.runners_contents[terminal_id] += output
                socket.emit('new_output', output, room=terminal_id)
            else:
                socket.sleep(0)

    def send_input(self, terminal_id, input):
        """Sending input to the runner.

        Args:
            terminal_id (str): Socket and runner identifier.
        """
        self[terminal_id].send_inputs(input)

    def send_runner_content(self, terminal_id):
        terminal_content = self.runners_contents[terminal_id]
        socket.emit('terminal_history', terminal_content, room=terminal_id)

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


@app.route("/runners")
def get_runners():
    """Serving the index page."""
    return runner_manager.runners


@socket.on("start_runner")
def start_runner(terminal_id):
    """Starting/Restarting the runner."""
    runner_manager.restart(terminal_id)


@socket.on("stop_runner")
def stop_runner(terminal_id):
    """Stopping the runner."""
    runner_manager.stop(terminal_id)


@socket.on("join_terminal")
def join_terminal(terminal_id):
    """Joining the terminal room."""
    join_room(terminal_id)
    runner_manager.send_runner_content(terminal_id)


@socket.on("leave_terminal")
def leave_terminal(terminal_id):
    """Leaving the terminal room."""
    leave_room(terminal_id)


@socket.on("get_terminal_content")
def get_terminal_content(terminal_id):
    """Leaving the terminal room."""
    runner_manager.send_runner_content(terminal_id)


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
