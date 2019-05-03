import './Terminal.css'
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
        this.state = {
            "socket": props.socket,
            "terminal_content": "",
            "active": false
        };
        this.state.socket.emit('join_terminal', this.id);
    }

    componentDidMount() {
        this.state.socket.on('new_output', (output) => {
            console.log(output);
            let output_html = this.ansi_converter.ansi_to_html(output);
            let decoded_html_output = this.entities.decode(output_html);
            this.setState({
                ...this.state,
                "terminal_content": this.state.terminal_content + decoded_html_output
            });
        });

        axios.get('/runner/' + this.id + '/active')
            .then(active => {
                this.setState({
                    ...this.state,
                    "active": active.data
                });

            })

        this.state.socket.on('terminal_history', (output) => {
            let output_html = this.ansi_converter.ansi_to_html(output);
            let decoded_html_output = this.entities.decode(output_html);
            this.setState({
                ...this.state,
                "terminal_content": decoded_html_output
            });
        });


        this.state.socket.on('is_active', (active) => {
            this.setState({
                ...this.state,
                "active": active
            });
        });
    }

    componentWillUnmount() {
        this.state.socket.emit('leave_terminal', this.id);
    }

    clear_terminal() {
        this.setState({
            ...this.state,
            "terminal_content": ""
        });
    }

    active_badge() {
        if (this.state.active)
            return <div className="active"></div>
        else
            return <div className="not_active"></div>
    }

    render() {
        return (
                <div className="terminal">
                    <div
                        className="terminal_body"
                        dangerouslySetInnerHTML={{__html: this.state.terminal_content}}>
                    </div>
                    <CommandForm id={this.id} socket={this.state.socket}/>
                    <div className="terminal_status_bar">
                        {this.active_badge.bind(this)()}
                    </div>
                </div>
        );
    }
}

export default Terminal