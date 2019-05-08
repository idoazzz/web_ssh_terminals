import React from 'react';
import ReactDOM from 'react-dom';
import queryString from 'query-string';
import socketIOClient from 'socket.io-client';
import Snackbar from '@material-ui/core/Snackbar';

import Terminal from './Terminal.jsx'


const WEBSOCKET_URL = "localhost:8000";

/**
 * Main terminal app page.
 * Contains terminal component and the control panel.
 */
class App extends React.Component {
    constructor(props) {
        /**
         * Parsing the terminal id from the url and open a websocket for the
         * terminal communication.
         */
        super(props);
        this.socket = socketIOClient(WEBSOCKET_URL)
        let parsed_args = queryString.parse(window.location.search);
        this.state = {
            terminal_id: parsed_args.terminal_id,
            error: ""
        };
    }

    start_terminal = () => {
        /**
         * Starting terminal through the web socket.
         * Starting terminal with start_runner event.
         */
        this.socket.emit('start_runner',
            this.state.terminal_id,
            "10.0.2.15",
            "osboxes",
            "osboxes.org");
    };

    stop_terminal = () => {
        /**
         * Stopping the current terminal through the websocket.
         * Stopping terminal with stop_runner event.
         */
        this.socket.emit('stop_runner', this.state.terminal_id);
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
         * Main components: Control panel and the terminal.
         */
        return (
            <div className="terminal_container">

                <Snackbar
                    anchorOrigin={{vertical: 'top', horizontal: 'center'}}
                    open={this.state.error !== ""}
                    onClick={this.close_snackbar}
                    message={<span id="message-id">{this.state.error}</span>}
                />

                <div className="blank"/>

                <Terminal id={this.state.terminal_id}
                          socket={this.socket}>
                </Terminal>

                <div className="control_panel">
                    <div>
                        <a onClick={this.start_terminal}>Start Terminal</a> |
                        <a onClick={this.stop_terminal}>Stop Terminal</a> |
                    </div>
                </div>

                <div className="blank"/>

            </div>
        );
    }
}

ReactDOM.render(<App/>, document.getElementById('app'));
