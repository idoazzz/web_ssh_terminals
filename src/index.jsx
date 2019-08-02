import React from 'react';
import ReactDOM from 'react-dom';
import queryString from 'query-string';
import socketIOClient from 'socket.io-client';
import Snackbar from '@material-ui/core/Snackbar';

import Terminal from './Terminal.jsx'


const WEBSOCKET_URL = "localhost:8000";

/**
 * Main session app page.
 * Contains session component and the control panel.
 */
class App extends React.Component {
    constructor(props) {
        /**
         * Parsing the session id from the url and open a websocket for the
         * session communication.
         */
        super(props);
        this.socket = socketIOClient(WEBSOCKET_URL)
        let parsed_args = queryString.parse(window.location.search);
        this.state = {
            session_id: parsed_args.session_id,
            error: ""
        };
    }

    start_session = () => {
        /**
         * Starting session through the web socket.
         * Starting session with start_session event.
         */
        this.socket.emit('start_session',
            this.state.session_id,
            "10.0.2.15",
            "osboxes",
            "osboxes.org");
    };

    stop_session = () => {
        /**
         * Stopping the current session through the websocket.
         * Stopping session with stop_session event.
         */
        this.socket.emit('stop_session', this.state.session_id);
    };


    open_snackbar = (error_message) => {
        /**
         * Handle a new error message with the snackbar.
         */
        this.setState({...this.state, error: error_message});
    };

    close_snackbar = () => {
        /**
         * Remove the error from the state.
         */
        this.setState({...this.state, error: ""});
    };

    componentDidMount() {
        /**
         * Listen for errors.
         */
        this.socket.on('error', (error) => {
            console.log(error)
            this.open_snackbar(error);
        });
    }


    render() {
        /**
         * Rendering the main app components.
         * Main components: Control panel and the session.
         */
        return (
            <div className="session_container">

                <Snackbar
                    anchorOrigin={{vertical: 'top', horizontal: 'center'}}
                    open={this.state.error !== ""}
                    onClick={this.close_snackbar}
                    message={<span id="message-id">{this.state.error}</span>}
                />

                <div className="blank"/>

                <Terminal id={this.state.session_id}
                          socket={this.socket}>
                </Terminal>

                <div className="control_panel">
                    <div>
                        <a onClick={this.start_session}>Start Terminal</a> |
                        <a onClick={this.stop_session}>Stop Terminal</a> |
                    </div>
                </div>

                <div className="blank"/>

            </div>
        );
    }
}

ReactDOM.render(<App/>, document.getElementById('app'));
