/**
 *
 * Entities
 *
 */

import React from 'react';
import { Container, Row, Col } from 'react-grid-system';
import { List } from 'semantic-ui-react';
import { Element } from 'react-scroll';

import PropTypes from 'prop-types';
// import styled from 'styled-components';

/* eslint-disable react/prefer-stateless-function */
const testData = [
  {
    id: 1,
    name: 'Brown Dog',
  },
  {
    id: 2,
    name: 'Ukraine',
  },
  {
    id: 3,
    name: 'Ireland',
  },
  {
    id: 4,
    name: 'Russia',
  },
  {
    id: 5,
    name: 'USA',
  },
];

const e = testData.map(en => <List.Item key={en.id}><a>{en.name}</a></List.Item>);

class Entities extends React.Component {
  render() {
    return (
      <Container>
        <Row>
          <Col sm={12}>
            <h2>Missing Entities</h2>
          </Col>
        </Row>
        <Row>
          <Col sm={10}>
            <Element
              name="entities"
              className="element"
              id="containerElement"
              style={{
                position: 'relative',
                height: '50vh',
                overflow: 'scroll',
                marginTop: '10px',
              }}
            >
              <List bulleted>
                {e}
                {this.props.entities.map(ent => (
                  <List.Item key={ent.id}><a>{ent.name}</a></List.Item>
                ))}
                {e}
                {e}
              </List>
            </Element>
          </Col>
        </Row>
      </Container>
    );
  }
}

Entities.propTypes = {
  entities: PropTypes.array,
};

export default Entities;
