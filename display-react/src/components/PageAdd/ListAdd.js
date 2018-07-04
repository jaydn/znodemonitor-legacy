import React, { Component } from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col, Card, CardBody, Input, Button, ListGroup, ListGroupItem } from 'reactstrap';
import { Redirect, Link } from 'react-router-dom';
import { ApiLocation } from '../../Config';

var dflt = {
    label: '',
    txid: '',
    idx: 0,
};

class ListAdd extends Component {
    constructor(props) {
        super(props);
        this.state = {
            nodes: [Object.assign({}, dflt)],
        }
        this.addNode = this.addNode.bind(this);
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
        fetch(ApiLocation + '/nodes', {
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
                this.props.setRedirect();

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

        var x = [];

        this.state.nodes.forEach((row, idx) => {
            x.push(
                <ListGroupItem color="secondary">
                    <Row>
                        <Col xs={12} md={3} className="mb-2">
                            <Input type="text" minLength={1} maxLength={32} name="label" onChange={this.handleInputChange.bind(this, idx)} value={this.state.nodes[idx].label} placeholder="label" />
                        </Col>
                        <Col xs={12} md={6} className="mb-2">
                            <Input type="text" minLength={64} maxLength={64} name="txid" onChange={this.handleInputChange.bind(this, idx)} value={this.state.nodes[idx].txid} placeholder="08e9e08bd050e337254d7bb056896b35dde1b0f44b24140443fc6788cfc1ec50" />
                        </Col>
                        <Col xs={12} md={2} className="mb-2">
                            <Input type="number" name="idx" onChange={this.handleInputChange.bind(this, idx)} value={this.state.nodes[idx].idx} />
                        </Col>
                        <Col xs={1}>
                            <Button color="danger" onClick={this.removeNode.bind(this, idx)}>x</Button>
                        </Col>
                    </Row>
                </ListGroupItem>
            );
        });

        return (
            <div>
                <Row className="mb-4">
                    <Col xs={3} md={1}>
                        <Button onClick={this.addNode}><span className="fa fa-plus" /></Button>
                    </Col>
                    <Col xs={3} md={1}>
                        <Button onClick={this.submitNodes.bind(this)}>Submit</Button>
                    </Col>
                </Row>
                <ListGroup className="mb-4">
                    {x}
                </ListGroup>
            </div>
        );
    }
}

export default ListAdd;