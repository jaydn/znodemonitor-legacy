import React, { Component } from 'react';
import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Link } from 'react-router-dom';

import zcoin from '../zcoin.svg';

class ZnmNavbar extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isOpen: false,
    };

    this.toggle = this.toggle.bind(this);
    this.onLogout = this.onLogout.bind(this);
  }

  toggle() {
    this.setState({
      isOpen: !this.state.isOpen,
    });
  }

  onLogout() {
    console.log('onLogout from ZnmNavbar ran');
    this.props.setToken(null);
    window.location = '/login'; // TODO lol
  }

  render() {
    var items = this.props.userInfo.token != null ?
      (
        <Nav className="ml-auto" navbar>
          <NavItem>
            <NavLink tag={Link} to="/overview"><span className="fa fa-server" /> Overview</NavLink>
          </NavItem>
          <NavItem>
            <NavLink tag={Link} to="/add"><span className="fa fa-plus" /> Add</NavLink>
          </NavItem>
          <NavItem>
            <NavLink tag={Link} to="/settings"><span className="fa fa-cog" /> Settings</NavLink>
          </NavItem>
          <NavItem>
            <NavLink href="#" onClick={this.onLogout}><span className="fa fa-sign-out" /> Logout</NavLink>
          </NavItem>
        </Nav>
      ) : (
        <Nav className="ml-auto" navbar>
          <NavItem>
            <NavLink tag={Link} to="/login"><span className="fa fa-sign-in" /> Login</NavLink>
          </NavItem>
          <NavItem>
            <NavLink tag={Link} to="/register"><span className="fa fa-user-plus" /> Register</NavLink>
          </NavItem>
        </Nav>
      );

    return (
      <div>
        <Navbar color="dark" dark expand="md" className="mb-4">
          <NavbarBrand>
            <img height="30" src={zcoin} className="d-inline-block align-top" alt="" />
          </NavbarBrand>
          <NavbarToggler onClick={this.toggle} />
          <Collapse isOpen={this.state.isOpen} navbar>
            {items}
          </Collapse>
        </Navbar>
      </div>
    );
  }
}

export default ZnmNavbar;