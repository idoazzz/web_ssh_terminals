import './app.css'
import axios from "axios";
import React, {Component} from 'react'
import {XmlEntities} from 'html-entities';
import {default as AnsiUp} from 'ansi_up';
import CommandForm from "./CommandForm.jsx";

const entities = new XmlEntities();
const ansi_converter = new AnsiUp();
/**
 * Terminal component holds the interactive session with the actual ssh runner
 * on the server. The ssh runner is connected to the target machine.
 * The received data (through the websocket) is displayed after it was parsed
 * from ansi to html tags.
 */
class Terminal extends Component {
    constructor(props) {
        /**
         * Receive the terminal id and the parent component websocket.
         * Initialize the terminal state - terminal content, and active flag.
         * Emit through the websocket that the user joined to terminal room.
         */
        super(props);
        this.id = props.id;
        this.socket = props.socket;
        this.state = {
            terminal_content: "",
            active: false
        };
        this.socket.emit('join_terminal', this.id);
        this.update_active_state();
    }

    update_active_state = () => {
        /**
         * Update the active state of the terminal through the active endpoint.
         */
        axios.get(`/runner/${this.id}/active`)
            .then(active => {
                this.setState({
                    ...this.state,
                    active: active.data
                });
        });
    };

    receive_new_output = (output, flush) => {
        /**
         * Get new output from the terminal, convert it from ansi to html tags,
         * and set the terminal content new state.
         * @param {string} output: New terminal output.
         */
        let output_html = ansi_converter.ansi_to_html(output);
        let decoded_html_output = entities.decode(output_html);
        let new_content = decoded_html_output;

        if(!flush)
            new_content = this.state.terminal_content + new_content;

        this.setState({
            ...this.state,
            terminal_content: new_content
        });
    };

    componentDidMount() {
        /**
         * Loading all the websocket listeners.
         * Listen for new_output event the indicates for new terminal output.
         * Listen for terminal_history event the indicates for receiving all
         * terminal history.
         * Listen for is_active event the updates the active state, this event
         * occurring when the terminal starts and ends.
         */
        this.socket.on('new_output', (output) => {
            this.receive_new_output(output, false);
        });

        this.socket.on('terminal_history', (output) => {
            this.receive_new_output(output, true);
        });

        this.socket.on('is_active', (active) => {
            this.setState({
                ...this.state,
                active: active
            });
        });
    }

    componentWillUnmount() {
    }

    active_badge = () => {
        /**
         * Render a new active element according to the active state.
         */
        if (this.state.active)
            return <div className="active"></div>
        return <div className="not_active"></div>
    };

    render() {
        return (
                <div className="terminal">

                    <div className="terminal_body"
                         dangerouslySetInnerHTML={
                             {__html: this.state.terminal_content}
                         }
                    />

                    <CommandForm id={this.id} socket={this.socket}/>

                    <div className="terminal_status_bar">
                        {this.active_badge()}
                    </div>

                </div>
        );
    }
}

export default Terminal