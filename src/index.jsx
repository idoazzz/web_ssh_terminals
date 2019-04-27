import React from 'react';
import ReactDOM from 'react-dom';
import queryString from 'query-string';

import Terminal from './Terminal.jsx'

class App extends React.Component {

    constructor(props){
        super(props);
        let url = window.location.search;
        let parsed_args = queryString.parse(url);
        this.state = {
            end_point: "localhost:8000",
            terminal_id: parsed_args.terminal_id
        };
    }

    render() {
        return (
            <div>
               <Terminal id={this.state.terminal_id}
                         end_point={ this.state.end_point }>
               </Terminal>
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
