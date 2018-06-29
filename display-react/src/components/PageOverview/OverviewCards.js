import React from 'react';

import { Card, CardBody, CardHeader } from 'reactstrap';

const GenericCard = (props) => {
    return (
        <Card color="dark" className="mb-4">
            <CardHeader><strong className={"text-"+props.color}>{props.head}</strong></CardHeader>
            <CardBody>
                {props.amt}
            </CardBody>
        </Card>
    );
}

export const EnabledCard = (props) => {
    return (
        <GenericCard color="success" head="Enabled" amt={props.amt} />
    );
};

export const AttentionCard = (props) => {
    return (
        <GenericCard color="warning" head="Require Attention" amt={props.amt} />
    );
};
