import React, { Component } from 'react';
//import { Container, Button } from 'reactstrap';
import { Switch, Route, Redirect } from 'react-router-dom';
import ZnmNavbar from './components/ZnmNavbar';
import OverviewContainer from './components/PageOverview/OverviewContainer';
import LoginContainer from './components/PageLogin';
import RegisterContainer from './components/PageRegister';
import SettingsContainer from './components/PageSettings/SettingsContainer';
import AddContainer from './components/PageAdd/AddContainer';
import NodeContainer from './components/PageNode/NodeContainer';
import NoMatch from './components/Errors';

import './bootstrap.min.css';
import 'react-table/react-table.css';

/*const PrivateRoute = ({ component: Component, ...rest }) => (
  <Route {...rest} render={(props) => (
    localStorage.getItem('token') !== null
      ? <Component {...props} />
      : <Redirect to={{
          pathname: '/login',
          //state: { from: props.location }
        }} />
  )} />
)*/

const Index = () => {
  if(localStorage.getItem('token') !== null) {
    return <Redirect to='/overview' />;
  } else {
    return <Redirect to='/login' />;
  }
};

class App extends Component {
  constructor() {
    super();
    this.state = {
      userInfo: {
        token: localStorage.getItem('token'),
      },
    };
    this.setToken = this.setToken.bind(this);
  }

  setToken(tkn) {
    if(tkn === null) { // TODO for some reason passing null to setItem would just set to string "null"
      localStorage.removeItem('token');
    } else {
      localStorage.setItem('token', tkn);
    }

    var uI = this.state.userInfo;
    uI.token = tkn;
    this.setState({
      userInfo: uI,
    });
  }

  render() {
    return (
      <div>
        <ZnmNavbar userInfo={this.state.userInfo} setToken={this.setToken}/>
        <Switch>
        <Route exact path='/' component={Index} />
        <Route exact path='/overview' render={()=><OverviewContainer userInfo={this.state.userInfo}/>} />
        <Route exact path='/add' render={()=><AddContainer userInfo={this.state.uesrInfo}/>} />
        <Route exact path='/settings' render={()=><SettingsContainer userInfo={this.state.userInfo}/>} />
        <Route exact path='/login' render={()=><LoginContainer setToken={this.setToken} />} />
        <Route exact path='/register' render={()=><RegisterContainer setToken={this.setToken} />} />
        <Route exact path='/node/:id' component={NodeContainer} />
        <Route component={NoMatch} />
        </Switch>
      </div>
    );
  }
}

export default App;
