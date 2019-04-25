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
        this.entities = new XmlEntities()
        this.ansi_converter = new AnsiUp();;
        this.state = {
            "socket": socketIOClient(props.end_point),
            "terminal_content": ""
        };
    }

    componentDidMount(){
      this.state.socket.on('new_output', (output) => {
          let output_html = this.ansi_converter.ansi_to_html(output);
          let decoded_html_output = this.entities.decode(output_html);
          this.setState({
              ...this.state,
              "terminal_content": this.state.terminal_content  + decoded_html_output
          });
      });
    }

    start_terminal() {
        axios.get(`/runner/start`)
          .then(res => {});
    }

    stop_terminal() {
        axios.get(`/runner/stop`)
          .then(res => {});
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
                    <a href='#' onClick={ this.start_terminal }>Start Terminal</a> |
                    <a href='#' onClick={ this.stop_terminal }>Stop Terminal</a> |
                    <a href='#' onClick={ this.clear_terminal.bind(this) }>Clear</a>
                </div>
                <div
                    className="terminal_body"
                    dangerouslySetInnerHTML={{__html: this.state.terminal_content}}>
                </div>
                <CommandForm socket={this.state.socket}/>
            </div>
        );
    }
}

export default Terminal