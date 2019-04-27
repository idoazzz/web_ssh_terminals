import './Terminal.css'
import axios from "axios";
import React, { Component } from 'react'
import { XmlEntities } from 'html-entities';
import { default as AnsiUp } from 'ansi_up';
import CommandForm from "./CommandForm.jsx";
import socketIOClient from 'socket.io-client';

class Terminal extends Component {

    constructor(props) {
        super(props);
        this.id = props.id;
        this.entities = new XmlEntities();
        this.ansi_converter = new AnsiUp();;
        this.state = {
            "socket": socketIOClient(props.end_point),
            "terminal_content": ""
        };
        this.state.socket.emit('join_terminal', this.id);
    }

    componentDidMount(){
      this.state.socket.on('new_output', (output) => {
          console.log(output)
          let output_html = this.ansi_converter.ansi_to_html(output);
          let decoded_html_output = this.entities.decode(output_html);
          this.setState({
              ...this.state,
              "terminal_content": this.state.terminal_content  + decoded_html_output
          });
      });

      this.state.socket.on('terminal_history', (output) => {
          console.log(output)
          let output_html = this.ansi_converter.ansi_to_html(output);
          let decoded_html_output = this.entities.decode(output_html);
          this.setState({
              ...this.state,
              "terminal_content": decoded_html_output
          });
      });
    }

    componentWillUnmount() {
        console.log("Disconnecting...")
        this.state.socket.emit('leave_terminal', this.id);
    }

    start_terminal() {
        this.state.socket.emit('start_runner', this.id);
    }

    stop_terminal() {
        this.state.socket.emit('stop_runner', this.id);
    }

    clear_terminal(){
        this.setState({
            ...this.state,
            "terminal_content": ""
        });
    }

    render() {
        return (
            <div className="terminal">
                <div>
                    <a onClick={ this.get_content.bind(this) }>Get Terminal Content</a> |
                    <a onClick={ this.start_terminal.bind(this) }>Start Terminal</a> |
                    <a onClick={ this.stop_terminal.bind(this) }>Stop Terminal</a> |
                    <a onClick={ this.clear_terminal.bind(this) }>Clear</a>
                </div>
                <div
                    className="terminal_body"
                    dangerouslySetInnerHTML={{__html: this.state.terminal_content}}>
                </div>
                <CommandForm id={this.id} socket={this.state.socket}/>
            </div>
        );
    }
}

export default Terminal