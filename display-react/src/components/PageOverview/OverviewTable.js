import React, { Component } from 'react';
//import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import { Card, CardBody, CardHeader, Button } from 'reactstrap';
import { Link } from 'react-router-dom';
import ReactTable from 'react-table';

class OverviewTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      removeMode: false,
    };
    this.toggleRemoveMode = this.toggleRemoveMode.bind(this);
  }

  toggleRemoveMode() {
    this.setState({
      removeMode: !this.state.removeMode,
    });
  }

  render() {
    var columns = [
      {
        id: 'lbl',
        Header: 'Label',
        accessor: d => <Link to={"/node/" + d.id}>{d.label}</Link>,
      },
      {
        Header: 'Status',
        accessor: 'node_status',
      },
      {
        Header: 'IP Address',
        accessor: 'node_ip',
      },
      {
        id: 'node_last_paid_block',
        Header: 'Last Paid',
        accessor: d => d.node_last_paid_block === 0 ? 'Never' : d.node_last_paid_block,
      },
      {
        id: 'node_last_seen',
        Header: 'Last Seen',
        accessor: d => d.node_last_seen === 0 ? 'Never' : new Date(d.node_last_seen * 1000).toLocaleString(),
      }
    ];

    if (this.state.removeMode) {
      columns.push({
        id: 'delete_button',
        Header: 'Delete',
        accessor: d => <Button className="btn-sm" color="danger" onClick={() => { this.props.deleteNode(this.props.userInfo.token, d.id); this.props.updateTableData(); }}>{d.id}<span className="fa fa-trash" /></Button>,
      });
    }

    return (
      <Card color="dark">
        <CardHeader>Overview<Button className="float-sm-right btn-sm" color="danger" onClick={this.toggleRemoveMode}>Remove</Button></CardHeader>
        <CardBody>
          <ReactTable data={this.props.nodes} columns={columns} defaultPageSize={100} minRows={0} />
        </CardBody>
      </Card>
    );
  }
}

export default OverviewTable;