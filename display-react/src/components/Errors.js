import React from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Container, Row, Col, Card, CardHeader, CardBody } from 'reactstrap';
//import { Redirect } from 'react-router-dom';

const GenericError = (props) => {
  return (
    <Container>
      <Row>
        <Col xs={12} md={6}>
          <Card color="primary">
            <CardHeader>{props.head}</CardHeader>
            <CardBody>
              <p>{props.body}</p>
            </CardBody>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export const NoMatch = (props) => {
  return (
    <GenericError head="404" body="Route not found" />
  );
};

export default NoMatch;