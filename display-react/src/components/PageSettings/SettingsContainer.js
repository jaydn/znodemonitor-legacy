import React, { Component } from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col, Card, CardBody } from 'reactstrap';
import { Redirect } from 'react-router-dom';
import { SettingsDisplay } from './SettingsDisplay';

class SettingsContainer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      cooldown: 0,
      emailReward: false,
      beenFetched: false,
      sending: false,
    }
    this.handleInputChange = this.handleInputChange.bind(this);
    this.updateSettings = this.updateSettings.bind(this);
    this.onApply = this.onApply.bind(this);
  }

  updateSettings() {
    fetch('http://do-debian-sgp1-01.jaydncunningham.com:5000/settings', {
      headers: {
        'Authorization': 'Bearer ' + this.props.userInfo.token,
      }
    })
      .then((response) => {
        console.log(response);
        return response.ok ? response.json() : {};
      })
      .then((inpJson) => {
        console.log(inpJson);
        if (inpJson.hasOwnProperty('cooldown') && inpJson.hasOwnProperty('emailReward')) {
          this.setState({
            cooldown: inpJson.cooldown,
            emailReward: inpJson.emailReward,
            beenFetched: true,
          });
        }
      })
      .catch((reason) => {
        console.log(reason);
        this.setState({ alert: reason.message });
      })
  }

  onApply(e) {
    this.setState({ sending: true, });

    e.preventDefault();

    var formData = new FormData();
    formData.append('cooldown', this.state.cooldown);
    formData.append('emailReward', this.state.emailReward);


    fetch('http://do-debian-sgp1-01.jaydncunningham.com:5000/settings', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + this.props.userInfo.token,
        //'Content-Type': 'application/json',
      },
      body: formData,
    })
      .then((response) => {
        console.log(response);
        this.setState({ sending: false, });
        //return response.ok ? response.json() : {};
      })
      .catch((reason) => {
        console.log(reason);
        //this.setState({ alert: reason.message });
      })
  }

  componentDidMount() {
    this.updateSettings();
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
  }

  render() {
    if (localStorage.getItem("token") === null) {
      return (<Redirect to='/login' />);
    }

    var sending = this.state.sending ? <p>Sending...</p> : null;

    var x = this.state.beenFetched ?
      <SettingsDisplay
        onApply={this.onApply}
        handleInputChange={this.handleInputChange}
        cooldown={this.state.cooldown}
        emailReward={this.state.emailReward}
        sending={sending} />
      :
      <p>Loading...</p>;

    return (
      <Container>
        <Row>
          <Col xs={12} md={6}>
            <Card color="primary">
              <CardBody>
                {x}
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }
}

export default SettingsContainer;