import React, { Component } from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col, Card, CardBody } from 'reactstrap';
import { Redirect } from 'react-router-dom';
import NodeDisplay from './NodeDisplay';
import { ApiLocation } from '../../Config';

class NodeContainer extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: [],
      hasFetched: false,
    };

    this.populateData = this.populateData.bind(this);
  }

  componentDidMount() {
    this.populateData();
  }

  populateData() {
    var uid = this.props.match.params.id;
    fetch(ApiLocation + '/getnode/' + uid,
      {
        headers: {
          'Authorization': 'Bearer ' + localStorage.getItem('token'),
        },
      })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          console.log(response);
        }
      })
      .then((inpJson) => {
        this.setState({ data: inpJson, hasFetched: true, });
      });
  }

  render() {
    if (localStorage.getItem("token") === null) {
      return (<Redirect to='/login' />);
    }

    var x = this.state.hasFetched ? (<NodeDisplay data={this.state.data} />) : (null);

    return (
      <Container>
        <Row>
          <Col xs={12}>
            <Card color="primary">
              <CardBody style={{overflow: "auto"}}>
                {x}
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }
}

export default NodeContainer;