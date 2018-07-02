import React, { Component } from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col, Card, CardBody, Input, Button, ListGroup, ListGroupItem } from 'reactstrap';
import { Redirect, Link } from 'react-router-dom';
import ListAdd from './ListAdd';
import BulkAdd from './BulkAdd';

var dflt = {
  label: '',
  txid: '',
  idx: 0,
};

class AddContainer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: [Object.assign({}, dflt)],
      shouldRedir: false,
      entryStyle: false,
    }
    this.addNode = this.addNode.bind(this);
    this.toggleEntryStyle = this.toggleEntryStyle.bind(this);
    //this.submitNodes = this.submitNodes.bind(this);
  }

  handleInputChange(uid, event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    var nodes = this.state.nodes;
    nodes[uid][name] = value;

    this.setState({
      nodes: nodes,
    });
  }

  addNode() {
    var nodes = this.state.nodes;
    nodes.unshift(Object.assign({}, dflt));
    this.setState({ nodes: nodes });
  }

  removeNode(uid) {
    var nodes = this.state.nodes;
    nodes.splice(uid, 1);
    this.setState({ nodes: nodes });
  }

  submitNodes(e) {
    console.log(this.props);
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
        this.setState({ nodes: [], shouldRedir: true });
        //return response.ok ? response.json() : {};
      })
      .catch((reason) => {
        console.log(reason);
        //this.setState({ alert: reason.message });
      })
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

    if (this.state.shouldRedir) {
      return (<Redirect to='/overview' />);
    }

    var x = this.state.entryStyle ? <BulkAdd /> : <ListAdd />;

    return (
      <Container>
        <Row>
          <Col xs={12}>
            <Card color="primary">
              <CardBody>
                {x}
                <Row>
                  <Col xs={3} md={1}>
                    <Button onClick={this.toggleEntryStyle}>{this.state.entryStyle ? 'List' : 'Bulk'}</Button>
                  </Col>
                </Row>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }
}

export default AddContainer;