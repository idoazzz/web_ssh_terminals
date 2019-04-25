import React from 'react';
import ReactDOM from 'react-dom';

import Terminal from './Terminal.jsx'

class App extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            end_point: "localhost:8000"
        };

    }

    render() {
        return (
            <div>
               <Terminal end_point={ this.state.end_point }></Terminal>
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
