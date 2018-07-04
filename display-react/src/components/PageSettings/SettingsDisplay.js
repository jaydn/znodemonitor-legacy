import React from 'react';

import { Form, FormGroup, Label, Input, Button } from 'reactstrap';

export const SettingsDisplay = (props) => {
    return (
        <Form onSubmit={props.onApply}>
            <FormGroup>
                <Label for="cooldown">Alert Cooldown</Label>
                <Input type="number" min={0} max={86400} name="cooldown" id="cooldown" value={props.cooldown} onChange={props.handleInputChange} required />
            </FormGroup>

            <FormGroup check className="mb-3">
                <Label check>
                    <Input type="checkbox" id="emailReward" name="emailReward" checked={props.emailReward} onChange={props.handleInputChange} />{' '}
                    Email on reward
                </Label>
            </FormGroup>
    
            <Button color="success">Apply</Button>{props.sending}
        </Form>
    );
}