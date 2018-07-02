import React, { Component } from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col, Card, CardBody, Input, Button, FormGroup, Label, Alert } from 'reactstrap';
import { Redirect, Link } from 'react-router-dom';

class BulkAdd extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: '',
      alert: null,
    }
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

  submitNodes(e) {
    this.setState({ alert: null });
    console.log(this.state.nodes);

    if (this.state.nodes === "") {
      return;
    }

    var issues = [];

    this.state.nodes.split('\n').forEach((row, idx) => {
      if (row === "") {
        return;
      }
      var spl = row.split(' ');
      if (spl.length != 3) {
        issues.push(<p>{'Row #' + idx + ' has ' + spl.length + ' columns'}</p>);
        return;
      }
      let [lbl, txid, nidx] = spl;
      if (!lbl.match('^.{1,32}$')) {
        issues.push(<p>{'Row #' + idx + ' label invalid'}</p>);
      }
      if (!txid.match('^[a-z0-9]{64}$')) {
        issues.push(<p>{'Row #' + idx + ' txid invalid'}</p>);
      }
      if (!nidx.match('^\d+$')) {
        issues.push(<p>{'Row #' + idx + ' index invalid'}</p>);
      }

    });

    if (issues.length !== 0) {
      this.setState({ alert: issues });
      return;
    }
    /*console.log(this.props);
    e.preventDefault();
    console.log(this.state.nodes);
    console.log(JSON.stringify(this.state.nodes));
    fetch('http://do-debian-sgp1-01.jaydncunningham.com:5000/nodes', {
      method: 'POST',
      headers: {
        //TODO fix this BS
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(this.state.nodes),
    })
      .then((response) => {
        console.log(response);
        //this.setState({ nodes: [], shouldRedir: true });
        // this.props.setRedirect();

        //return response.ok ? response.json() : {};
      })
      .catch((reason) => {
        console.log(reason);
        //this.setState({ alert: reason.message });
      })*/
  }

  toggleEntryStyle() {
    this.setState({
      entryStyle: !this.state.entryStyle,
    });
  }

  render() {
    if (localStorage.getItem("token") === null) {
      return (<Redirect to='/login' />);
    }

    var alrt = this.state.alert !== null ?
      (
        <Row>
          <Col xs={12}>
            <Alert color="warning">{this.state.alert}</Alert>
          </Col>
        </Row>
      ) : null;

    return (
      <div>
        {alrt}
        <Row className="mb-4">
          <Col xs={3} md={1}>
            <Button onClick={this.submitNodes.bind(this)}>Submit</Button>
          </Col>
        </Row>
        <FormGroup>
          <Label for="nodes">Syntax: Label TXID Index</Label>
          <Input type="textarea"
            name="nodes"
            id="nodes"
            rows={10}
            placeholder="znode01 08e9e08bd050e337254d7bb056896b35dde1b0f44b24140443fc6788cfc1ec50 1"
            onChange={this.handleInputChange}
            value={this.state.nodes}
          />
        </FormGroup>
      </div>
    );
  }
}

export default BulkAdd;