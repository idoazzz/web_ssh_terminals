import os

import yaml
from attrdict import AttrDict
from flask import Flask, jsonify, render_template, request, session
from flask_socketio import SocketIO, join_room, leave_room

from sessions_manager import SessionsManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

socket = SocketIO(app,
                  static_url_path='/static',
                  logger=True,
                  engineio_logger=True,
                  async_mode="eventlet")

SESSIONS_CONFIG = "sessions_config.yml"


class SessionManagerBackgroundTask(SessionsManager):
    """Manage session session input and output.

    Managing the client session session with the server means that this class
    initiate a thread that listening for new output in the session.
    If we found new output, we emitting this output to the client through
    websocket. If the client want to send something to the session, it's
    passes here also.

    Attributes:
        sessions_listeners (dict): Contains threads that listening for new
        output.
    """
    FILTER_RULES = {
        "\\x1b": "\x1B",
        "\n": "<br>",
        "]0;": ""
    }

    def __init__(self):
        super(SessionManagerBackgroundTask, self).__init__()
        self.sessions_listeners = {}

        with open(SESSIONS_CONFIG) as sessions_config:
            config = sessions_config.read()
            self.config = AttrDict(yaml.load(config))

    @property
    def active_sessions(self):
        """Return the active sessions."""
        return self._sessions

    def restart(self, session_id, host, username, password):
        """Restart the session and the listening thread.

        Args:
            session_id (str): Socket and session identifier.
            host (str): Remote host.
            username (str): Target username.
            password (str): Target password.
        """
        if len(self.active_sessions) >= self.config.sessions_limit:
            socket.emit("error", "Cannot add new session. Limit has reached.",
                        room=session_id)
            return

        if not self.exists(session_id):
            self.load_session(session_id, host, username, password)
        else:
            self.stop(session_id)

        self.start(session_id)
        self.sessions_listeners[session_id] = socket. \
            start_background_task(self.listen_for_output, session_id)

        for command in self.config.startup_commands:
            self.send_input(session_id, command)

        socket.emit("is_active", True, room=session_id)

    def stop(self, session_id):
        """Stopping the listening thread and the session.

        Args:
            session_id (str): Socket and session identifier.
        """
        if self.exists(session_id):
            socket.emit("is_active", False, room=session_id)
            self.terminate_session(session_id)  # Will end the thread
            self.sessions_listeners[session_id] = None

    def listen_for_output(self, session_id):
        """Listen for new output and emitting to the client.

        Args:
            session_id (str): Socket and session identifier.
        """
        while self.exists(session_id):
            output = self[session_id].read_output()
            if output is not None:
                output = self.filter_output(output)
                socket.emit('new_output', output, room=session_id)
            else:
                socket.sleep(0)

    def send_input(self, session_id, command):
        """Sending input to the session.

        Args:
            session_id (str): Socket and session identifier.
            command (str): Input for the session.
        """
        if not self.exists(session_id):
            return

        self[session_id].send_inputs(command)

    def send_session_history(self, session_id):
        """Send the history of the session to a specific room."""

        if not self.exists(session_id):
            return

        session_content = self[session_id].output
        socket.emit('session_history', self.filter_output(session_content),
                    room=session_id)

    def filter_output(self, output):
        """Filtering the session output and adjust the output to the client.

        Args:
            output (str): Session output that need to be filtered.
        """
        for key, value in self.FILTER_RULES.items():
            output = output.replace(key, value)
        return output


session_manager = SessionManagerBackgroundTask()


@app.route("/")
def index():
    """Serving the index page."""
    return render_template('index.html')


@app.route("/session/<session_id>/active")
def is_active(session_id):
    """Serving the index page."""
    return jsonify(session_manager.exists(session_id))


@app.route("/sessions")
def get_sessions():
    """Serving the index page."""
    return session_manager.sessions


@socket.on("start_session")
def start_session(session_id, host, username, password):
    """Starting/Restarting the session."""
    session_manager.restart(session_id, host, username, password)


@socket.on("stop_session")
def stop_session(session_id):
    """Stopping the session."""
    session_manager.stop(session_id)


@socket.on("join_session")
def join_session(session_id):
    """Joining the session room."""
    join_room(session_id)
    session_manager.send_session_history(session_id)


@socket.on("leave_session")
def leave_session(session_id):
    """Leaving the session room."""
    leave_room(session_id)


@socket.on('new_input')
def handle_message(data):
    """Sending new input to the session."""
    session_manager.send_input(data["session_id"], data["command"])


@socket.on('disconnect')
def disconnect():
    pass


@socket.on('connect')
def connection():
    pass


if __name__ == '__main__':
    socket.run(app, host='127.0.0.1', port=8000, debug=True)
