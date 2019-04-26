import os

from flask import Flask, jsonify, render_template, request, session
from flask_socketio import SocketIO

from runners import Runner, RunnersManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

socket = SocketIO(app, logger=True, engineio_logger=True)

DEFAULT_RUNNER_PROCESS = "python /home/osboxes/projects/sandbox/example.py"


class RunnerManagerBackgroundTask(object):
    """Manage runner runner input and output.

    Managing the client runner session with the server means that this class
    initiate a thread that listening for new output in the runner.
    If we found new output, we emitting this output to the client through
    websocket. If the client want to send something to the runner, it's
    passes here also.

    Attributes:
        runners (RunnerManager): Runners manager.
        emitter_threads (dict): Contains threads that listening for new output.
    """
    FILTER_RULES = {
        "\\r": "",
        "\\n": "<br>",
        "\\x1b": "\x1B"
    }

    def __init__(self):
        self.emitter_threads = {}
        self.runners = RunnersManager()

    def load_runner(self, socket_id):
        """Load a new session runner."""
        self.runners.load_runner(socket_id, DEFAULT_RUNNER_PROCESS)

    def restart(self, socket_id):
        """Restart the runner and the listening thread."""
        if not self.runners.exists(socket_id):
            self.load_runner(socket_id)

        if self.runners.is_active(socket_id):
            self.stop(socket_id)

        self.runners.start(socket_id)
        self.emitter_thread[socket_id] = socket. \
            start_background_task(self.listen_for_output, socket_id)

    def stop(self, socket_id):
        """Stopping the listening thread and the runner."""
        if self.runners.is_active(socket_id):
            self.emitter_thread.kill()
            self.emitter_thread[socket_id] = None
            self.runners.terminate_runner(socket_id)

    def listen_for_output(self, socket_id):
        """Listen for new output and emitting to the client."""
        while self.runners.is_active(socket_id):
            output = self.runners[socket_id].read_output()
            if output is not None:
                output = self.filter_output(output)
                socket.emit('new_output', output, room=socket_id)
            else:
                socket.sleep(0)

    def send_input(self, socket_id, *inputs):
        """Sending input to the runner."""
        self.runners[socket_id].send_inputs(*inputs)

    def filter_output(self, output):
        """Filtering the runner output and adjust the output to the client."""
        for key, value in self.FILTER_RULES.items():
            output = output.replace(key, value)
        return output


runner_manager = RunnerManagerBackgroundTask()


@app.route("/")
def index():
    """Serving the index page."""
    return render_template('index.html')


@socket.on("start_runner")
def start_runner():
    """Starting/Restarting the runner."""
    runner_manager.restart(request.sid)


@socket.on("stop_runner")
def stop_runner():
    """Stopping the runner."""
    runner_manager.stop(request.sid)


@socket.on('new_input')
def handle_message(message):
    """Sending new input to the runner."""
    runner_manager.send_input(request.sid, message)


@socket.on('disconnect')
def disconnect():
    # runner.stop()
    pass


@socket.on('connect')
def connection():
    pass


if __name__ == '__main__':
    socket.run(app, host='127.0.0.1', port=8000, debug=True)
