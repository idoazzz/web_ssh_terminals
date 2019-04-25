import React, { Component } from 'react'
import './Terminal.css'

class CommandForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
        "socket": props.socket,
        "value": ""
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({...this.state,value: event.target.value});
  }

  handleSubmit(event) {
    this.send(this.state.value)
    event.preventDefault();
  }

  send(command){
      this.state.socket.emit('new_input', command);
  }

  render() {
    return (
      <form className="command_form" onSubmit={this.handleSubmit}>
        <label>
          <input className="command_input"
                 placeholder="$ Insert your command"
                 type="text"
                 value={this.state.value}
                 onChange={this.handleChange} />
        </label>
      </form>
    );
  }
}

export default CommandForm