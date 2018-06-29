import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col, Card, CardBody, Alert } from 'reactstrap';
import { Form, FormGroup, Label, Input, Button } from 'reactstrap';
//import { Redirect } from 'react-router-dom';

class LoginContainer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      alert: '',
      shouldRedir: false,

      email: '',
      password: '',
    }

    this.onLogin = this.onLogin.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
  }


  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
  }

  onLogin(e) {
    e.preventDefault();
    console.log('onLogin from LoginContainer');
    console.log(this.state.email + ':' + this.state.password);

    var formData = new FormData();
    formData.append('email', this.state.email);
    formData.append('password', this.state.password);


    fetch('http://do-debian-sgp1-01.jaydncunningham.com:5000/auth', {
      method: 'POST',
      body: formData,
    })
      .then((response) => {
        console.log(response);
        if (!response.ok) {
          this.setState({ alert: response.status + ': ' + response.statusText });
        }
        return response.ok ? response.json() : {};
      })
      .then((inpJson) => {
        console.log(inpJson);
        if (inpJson.hasOwnProperty('token')) {
          this.props.setToken(inpJson.token);
          this.setState({ shouldRedir: true });
        } else if (inpJson.hasOwnProperty('msg')) {
          this.setState({ alert: inpJson.msg });
        }
      })
      .catch((reason) => {
        console.log(reason);
        this.setState({ alert: reason.message });
      })
  }

  render() {
    if (this.state.shouldRedir) {
      return (
        <Redirect to='/overview' />
      );
    }

    var alrt = (<div />);
    if (this.state.alert !== '') {
      alrt = (
        <Row>
          <Col xs={12} md={6}>
            <Alert color="warning">{this.state.alert}</Alert>
          </Col>
        </Row>
      )
    }

    return (
      <Container>
        {alrt}
        <Row>
          <Col xs={12} md={6}>
            <Card color="primary">
              {/*<CardHeader><strong>Login</strong></CardHeader>*/}
              <CardBody>
                <Form onSubmit={this.onLogin}>
                  <FormGroup>
                    <Label for="email">Email</Label>
                    <Input type="email" minLength={3} maxLength={256} name="email" id="email" value={this.state.email} onChange={this.handleInputChange} placeholder="name@domain.tld" required />
                  </FormGroup>
                  <FormGroup>
                    <Label for="password">Password</Label>
                    <Input type="password" minLength={12} maxLength={256} name="password" id="password" value={this.state.password} onChange={this.handleInputChange} placeholder="********" required />
                  </FormGroup>
                  <Button color="success">Login</Button>
                </Form>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }
}

export default LoginContainer;