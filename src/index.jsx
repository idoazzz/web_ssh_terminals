import React from 'react';
import ReactDOM from 'react-dom';
import queryString from 'query-string';
import socketIOClient from 'socket.io-client';

import Terminal from './Terminal.jsx'

class App extends React.Component {

    constructor(props){
        super(props);
        let url = window.location.search;
        let parsed_args = queryString.parse(url);
        this.state = {
            socket: socketIOClient("localhost:8000"),
            terminal_id: parsed_args.terminal_id
        };
    }

    start_terminal() {
        this.state.socket.emit('start_runner', this.state.terminal_id, "10.0.2.15", "osboxes",
            "osboxes.org");
    }

    stop_terminal() {
        this.state.socket.emit('stop_runner', this.state.terminal_id);
    }

    render() {
        return (
            <div className="terminal_container">
                <div className="blank">
                </div>
                <Terminal id={this.state.terminal_id}
                         socket={ this.state.socket }>
               </Terminal>
                <div className="control_panel">
                    <div>
                        <a onClick={this.start_terminal.bind(this)}>Start
                            Terminal</a> |
                        <a onClick={this.stop_terminal.bind(this)}>Stop
                            Terminal</a> |
                    </div>
                </div>
                <div className="blank">
                </div>
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
