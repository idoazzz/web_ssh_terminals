import './app.css'
import axios from "axios";
import React, {Component} from 'react'
import {XmlEntities} from 'html-entities';
import {default as AnsiUp} from 'ansi_up';
import CommandForm from "./CommandForm.jsx";

class Terminal extends Component {

    constructor(props) {
        super(props);
        this.id = props.id;
        this.entities = new XmlEntities();
        this.ansi_converter = new AnsiUp();
        this.socket = props.socket;
        this.state = {
            "terminal_content": "",
            "active": false
        };
        this.socket.emit('join_terminal', this.id);
    }

    update_active_state(){
        axios.get('/runner/' + this.id + '/active')
            .then(active => {
                this.setState({
                    ...this.state,
                    "active": active.data
                });
        });
    }

    componentDidMount() {
        this.update_active_state()

        this.socket.on('new_output', (output) => {
            let output_html = this.ansi_converter.ansi_to_html(output);
            let decoded_html_output = this.entities.decode(output_html);
            this.setState({
                ...this.state,
                "terminal_content": this.state.terminal_content + decoded_html_output
            });
        });

        this.socket.on('terminal_history', (output) => {
            let output_html = this.ansi_converter.ansi_to_html(output);
            let decoded_html_output = this.entities.decode(output_html);
            this.setState({
                ...this.state,
                "terminal_content": decoded_html_output
            });
        });

        this.socket.on('is_active', (active) => {
            this.setState({
                ...this.state,
                "active": active
            });
        });
    }

    componentWillUnmount() {
        this.socket.emit('leave_terminal', this.id);
    }

    active_badge = () => {
        if (this.state.active)
            return <div className="active"></div>
        return <div className="not_active"></div>
    };

    render() {
        return (
                <div className="terminal">
                    <div
                        className="terminal_body"
                        dangerouslySetInnerHTML={{__html: this.state.terminal_content}}>
                    </div>
                    <CommandForm id={this.id} socket={this.socket}/>
                    <div className="terminal_status_bar">
                        {this.active_badge()}
                    </div>
                </div>
        );
    }
}

export default Terminal