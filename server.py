import eventlet

from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO

from runners import Runner

eventlet.monkey_patch()

app = Flask(__name__)
socket = SocketIO(app, logger=True, engineio_logger=True)

DEFAULT_RUNNER_PROCESS = "python /home/osboxes/projects/sandbox/example.py"


class RunnerBackgroundTask(object):
    """Manage runner runner input and output.

    Managing the client runner session with the server means that this class
    initiate a thread that listening for new output in the runner.
    If we found new output, we emitting this output to the client through
    websocket. If the client want to send something to the runner, it's
    passes here also.

    Attributes:
        emitter_thread (GreenThread): Thread that listening for new output.
    """
    FILTER_RULES = {
        "\\r": "",
        "\\n": "<br>",
        "\\x1b": "\x1B"
    }

    def __init__(self, runner_name="default_runner"):
        self.emitter_thread = None
        self.runner = Runner(runner_name, DEFAULT_RUNNER_PROCESS)

    def restart(self):
        """Restart the runner and the listening thread."""
        if self.runner.active:
            self.stop()

        self.runner.start()
        self.emitter_thread = eventlet.spawn(self.listen_for_output)

    def set_new_runner(self, run_command):
        self.runner = Runner("standalone_runner", run_command)

    def stop(self):
        """Stopping the listening thread and the runner."""
        if self.runner.active:
            self.emitter_thread.kill()
            self.emitter_thread = None
            self.runner.exit()
            self.runner = None

    def listen_for_output(self):
        """Listen for new output and emitting to the client."""
        while self.runner.active:
            output = self.runner.read_output()
            if output is not None:
                output = self.filter_output(output)
                socket.emit('new_output', output)
            else:
                eventlet.sleep(1)

    def send_input(self, *inputs):
        """Sending input to the runner."""
        self.runner.send_inputs(*inputs)

    def filter_output(self, output):
        """Filtering the runner output and adjust the output to the client."""
        for key, value in self.FILTER_RULES.items():
            output = output.replace(key, value)
        return output


runner = RunnerBackgroundTask()


@app.route("/")
def index():
    """Serving the index page."""
    return render_template('index.html')


@app.route("/runner/start/")
def start_runner():
    """Starting/Restarting the runner."""
    runner.restart()
    return jsonify("Shell on")


@app.route("/runner/stop")
def stop_runner():
    """Stopping the runner."""
    runner.stop()
    return jsonify("Shell off")


@socket.on('new_input')
def handle_message(message):
    """Sending new input to the runner."""
    runner.send_input(message)


@socket.on('disconnect')
def disconnect():
    runner.stop()


if __name__ == '__main__':
    socket.run(app, host='127.0.0.1', port=8000, debug=True)

# TODO: Handle multiple tabs
# TODO: Handle disconnections
# TODO: Scroll down automatically.
# TODO: Handle runner names, and initiating the runner.
