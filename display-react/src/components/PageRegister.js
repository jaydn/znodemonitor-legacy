import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col, Card, CardBody, Alert } from 'reactstrap';
import { Form, FormGroup, Label, Input, Button } from 'reactstrap';
import { ApiLocation } from '../Config';
//import { Redirect } from 'react-router-dom';

class RegisterContainer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      inviteKey: false,

      alert: '',
      shouldRedir: false,

      email: '',
      password: '',
      passwordv: '',
      invkey: '',
    }

    this.onLogin = this.onLogin.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  componentDidMount() {
    fetch(ApiLocation + '/info/register').then((response) => {
      if (response.ok) {
        return response.json();
      }
    }).then((inpJson) => {
      console.log(inpJson);
      this.setState({ inviteKey: inpJson['inviteRequired'] });
    });
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
    this.setState({alert: ''});

    e.preventDefault();
    console.log('onLogin from LoginContainer');
    console.log(this.state.email + ':' + this.state.password);

    var formData = new FormData();
    formData.append('email', this.state.email);
    formData.append('password', this.state.password);
    formData.append('invkey', this.state.invkey);


    fetch(ApiLocation + '/register', {
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

    var isReady = (this.state.password === this.state.passwordv) && (this.state.password.length > 0);

    var x = this.state.inviteKey ? (
      <FormGroup>
        <Label for="invkey">Invite Key</Label>
        <Input type="text" name="invkey" id="invkey" value={this.state.invkey} onChange={this.handleInputChange} required />
      </FormGroup>
    ) : null;

    var y = (this.state.inviteKey && this.state.alert === "") ? (
      <Alert color='info'>
        This is not a public instance. Please go to <a className="text-primary" href="https://znodemonitor.com/">znodemonitor.com</a> if you were not directed here explicitly.
      </Alert>
    ) : null;

    return (
      <Container>
        {alrt}
        <Row>
          <Col xs={12} md={6}>
            {y}
            <Card color="primary">
              {/*<CardHeader><strong>Login</strong></CardHeader>*/}
              <CardBody>
                <Form onSubmit={this.onLogin}>
                  {x}
                  <FormGroup>
                    <Label for="email">Email</Label>
                    <Input type="email" minLength={3} maxLength={256} name="email" id="email" value={this.state.email} onChange={this.handleInputChange} placeholder="name@domain.tld" required />
                  </FormGroup>
                  <FormGroup>
                    <Label for="password">Password</Label>
                    <Input type="password" minLength={12} maxLength={256} name="password" id="password" value={this.state.password} onChange={this.handleInputChange} placeholder="********" required />
                  </FormGroup>
                  <FormGroup>
                    <Label for="passwordv">Password (again)</Label>
                    <Input type="password" minLength={12} maxLength={256} name="passwordv" id="passwordv" value={this.state.passwordv} onChange={this.handleInputChange} placeholder="********" required />
                  </FormGroup>
                  <Button color="success" disabled={!isReady}>Register</Button>
                </Form>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }
}

export default RegisterContainer;