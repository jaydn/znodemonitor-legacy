import React, { Component } from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col } from 'reactstrap';
import { Redirect } from 'react-router-dom';
import OverviewTable from './OverviewTable';
import { EnabledCard, AttentionCard } from './OverviewCards';
//import Overview
import { ApiLocation } from '../../Config';

class OverviewContainer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: [],
      nodesFetched: false,
    }
    this.updateTableData = this.updateTableData.bind(this);
  }

  deleteNode(tkn, uid) {
    fetch(ApiLocation + '/delete', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + tkn,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify([uid]),
    }).then((response) => {
      console.log(response);
    })
  }

  componentDidMount() {
    this.updateTableData();
    this.timerID = setInterval(this.updateTableData, 10000);
  }

  componentWillUnmount() {
    clearInterval(this.timerID);
  }

  updateTableData() {
    fetch(ApiLocation + '/nodes', {
      headers: {
        'Authorization': 'Bearer ' + this.props.userInfo.token,
      }
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          return [];
        }
      })
      .then((inpJson) => {
        //inpJson = inpJson.length === 0 ? [{}] : inpJson;
        this.setState({
          nodes: inpJson,
          nodesFetched: true,
        })
      });
  }

  render() {
    if (localStorage.getItem("token") === null) {
      return (<Redirect to='/login' />);
    }

    var enabledAmt = 0;
    var attentionAmt = 0;
    // TODO gotta be better way to do this
    this.state.nodes.forEach((row) => {
      if (row.node_status === 'ENABLED') {
        enabledAmt++;
      }
    });
    attentionAmt = this.state.nodes.length - enabledAmt;

    var cards = (this.state.nodesFetched && this.state.nodes.length !== 0)
      ?
      (
        <Row>
          <Col xs={12} md={3}>
            <EnabledCard amt={enabledAmt} />
          </Col>
          <Col xs={12} md={3}>
            <AttentionCard amt={attentionAmt} />
          </Col>
        </Row>
      ) : (null);

    var table = this.state.nodes.length !== 0 ?
      <OverviewTable deleteNode={this.deleteNode}
        userInfo={this.props.userInfo}
        updateTableData={this.updateTableData}
        nodes={this.state.nodes} /> :
      (this.state.nodesFetched ?
        <Redirect to='/add'/>
        : <p>Loading...</p>);

    return (
      <Container>
        {cards}
        <Row>
          <Col xs={12}>
            {table}
          </Col>
        </Row>
      </Container>
    );
  }
}

export default OverviewContainer;