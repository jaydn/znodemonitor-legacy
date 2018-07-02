import React, { Component } from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Table } from 'reactstrap';

class NodeDisplay extends Component {
  render() {
    var x = [];
    
    for (const [key, value] of Object.entries(this.props.data)) {
        x.push((
            <tr>
                <th>{key}</th>
                <td>{value}</td>
            </tr>
        ));
    }

    return (
        <Table dark className="text-white">
            <tbody>
                {x}
            </tbody>
        </Table>
    );
  }
}

export default NodeDisplay;