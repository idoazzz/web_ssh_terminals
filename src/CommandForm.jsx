import React, {Component} from 'react'

/**
 * Command form is an input the handles the user shell commands.
 * Each command that the user insert piped into the web socket and to the
 * remote machine through ssh runner.
 */
class CommandForm extends Component {
    constructor(props) {
        /**
         * Initialize terminal id and the parent component websocket.
         * Also, the value state represent the user input.
         */
        super(props);
        this.id = props.id;
        this.state = {
            socket: props.socket,
            value: ""
        };
    }

    handleChange = (event) => {
        /**
         * Handle any change in the user command input, and set the new state.
         */
        this.setState({...this.state, value: event.target.value});
    };

    handleSubmit = (event) => {
        /**
         * Submit the command through the websocket.
         */
        this.send(this.state.value);
        event.preventDefault();
    };

    send = (command) => {
        /**
         * Sending the command to the websocket with the new_input event.
         * @param {string} command: User command.
         */
        this.state.socket.emit('new_input',{
                "command": command,
                "terminal_id": this.id
        });
        this.setState({...this.state, value: ""});
    };

    render() {
        return (
            <form className="command_form" onSubmit={this.handleSubmit}>

                <input autoFocus className="command_input"
                       placeholder="$ Insert your command"
                       type="text"
                       value={this.state.value}
                       onChange={this.handleChange}/>

            </form>
        );
    }
}

export default CommandForm