/**
 *
 * Details
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
// import styled from 'styled-components';

import { Container, Row } from 'react-grid-system';
import { Label } from 'semantic-ui-react';
import { Element } from 'react-scroll';

/* eslint-disable react/prefer-stateless-function */
class Details extends React.Component {
  constructor(props) {
    super(props);

  }
  render() {
    return (
      <div>
        <Container>
          <Row>
            <Label color="black">Entity: {this.props.items.entity}</Label>
          </Row>
          <Row>
            <Label color="black">MD5: {this.props.items.MD5}</Label>
          </Row>
          <Row>
            <Label color="black">REF: {this.props.items.REF}</Label>
          </Row>
          <Row>
            <Label color="black">Segment ID: {this.props.items.SegmentId}</Label>
          </Row>
          <Row>
            <Label color="black">Frame No: {this.props.items.Frame}</Label>
          </Row>
          <Row>
            <Label color="green">
              Canonical Mentions:
              <Element
                name="entities"
                className="element"
                id="containerElement"
                style={{
                  position: 'relative',
                  height: '15vh',
                  overflow: 'scroll',
                }}
              >
                <ul>
                  {this.props.items.canonicalMentions.map(m => (
                    <li>{m}<a href="#">Replace</a>, <a href="#">Remove</a></li>
                  ))}
                </ul>
              </Element>
            </Label>
          </Row>
        </Container>
      </div>
    );
  }
}

Details.propTypes = {
  items: PropTypes.object,
};

export default Details;
