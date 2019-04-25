import React from 'react';
import ReactDOM from 'react-dom';

import Shell from './Shell.jsx'

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
               <Shell end_point={ this.state.end_point }></Shell>
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
