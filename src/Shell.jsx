import './Shell.css'
import axios from "axios";
import React, { Component } from 'react'
import { XmlEntities } from 'html-entities';
import { default as AnsiUp } from 'ansi_up';
import CommandForm from "./CommandForm.jsx";
import socketIOClient from 'socket.io-client';

class Shell extends Component {

    constructor(props) {
        super(props);
        this.entities = new XmlEntities()
        this.ansi_converter = new AnsiUp();;
        this.state = {
            "socket": socketIOClient(props.end_point),
            "shell_content": ""
        };
    }

    componentDidMount(){
      this.state.socket.on('new_output', (output) => {
          let output_html = this.ansi_converter.ansi_to_html(output);
          let decoded_html_output = this.entities.decode(output_html);
          this.setState({
              ...this.state,
              "shell_content": this.state.shell_content  + decoded_html_output
          });
      });
      this.start_shell()
    }

    start_shell() {
        axios.get(`/runner/start`)
          .then(res => {});
    }

    stop_shell() {
        axios.get(`/runner/stop`)
          .then(res => {});
    }

    clear_shell(){
        this.setState({
            ...this.state,
            "shell_content": ""
        });
    }

    render() {
        return (
            <div className="shell">
                <div>
                    <a href='#' onClick={ this.start_shell }>Start Shell</a> |
                    <a href='#' onClick={ this.stop_shell }>Stop Shell</a> |
                    <a href='#' onClick={ this.clear_shell.bind(this) }>Clear</a>
                </div>
                <div
                    className="shell_body"
                    dangerouslySetInnerHTML={{__html: this.state.shell_content}}>
                </div>
                <CommandForm socket={this.state.socket}/>
            </div>
        );
    }
}

export default Shell