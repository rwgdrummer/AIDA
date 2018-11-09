/**
 *
 * CanonicalPage
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Helmet } from 'react-helmet';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';

import { Container, Row, Col } from 'react-grid-system';
import { Button, Divider } from 'semantic-ui-react';

import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';

import Panel from '../../components/Panel';
import Entities from '../../components/Entities';
import makeSelectCanonicalPage from './selectors';
import reducer from './reducer';
import saga from './saga';
import { getTest } from './actions';

/* eslint-disable react/prefer-stateless-function */
export class CanonicalPage extends React.Component {
  componentDidMount() {
    //TODO add the test call to try to pass to props
    // this.props.getTestJSON();
    //this.props.getTestJSON();
    console.log('Component Did Mount');
    //this.props.getTestJSON();
    console.log('Attemted to call getTestJSON');
    // console.log(this.props);
    // console.log(getTest());
  }
  handleChange = (name) => (event) => {
    this.setState({
      [name]: event.target.value,
    });
  };

  render() {
    console.log('Render Area');
    return (
      <div>
        <Helmet>
          <title>Add Canonicals</title>
          <meta
            name="Canonical"
            content="Page that creates Canonical Mentions"
          />
        </Helmet>
        <Container>
          <Row>
            <Divider hidden />
          </Row>
          <Row>
            <Col sm={3}>
              <Entities entities={[{ name: '12', id: 10, }, { name: 'Poles', id: 20, }, { name: 'Bears', id: 21, }]} />
            </Col>
            <Col sm={9}>
              <Panel items={{ entity: 'Bear', MD5: 'aklsdjfasdlkfjkwjdf', REF: 'aklsdjfiomwcldifsojweREF', SegmentId: '1823998123', Frame: '192', canonicalMentions: ['Tree', 'Lap Dog', 'Lap Dog1', 'Lap Dog2', 'Lap Dog3', 'Lap Dog4'] }} />
            </Col>

          </Row>

        </Container>
      </div>
    );
  }
}

CanonicalPage.propTypes = {
  // getTestJSON: PropTypes.func.isRequired,

};

const mapStateToProps = createStructuredSelector({
  canonicalpage: makeSelectCanonicalPage(),
});

function mapDispatchToProps(dispatch) {
  console.log('mapDispatchtoProps');
  return {
    //getTestJSON: () => dispatch(getTest()),
  };
}

const withConnect = connect(
  mapStateToProps,
  mapDispatchToProps,
);

const withReducer = injectReducer({ key: 'canonicalPage', reducer });
const withSaga = injectSaga({ key: 'canonicalPage', saga });

export default compose(
  withReducer,
  withSaga,
  withConnect,
)(CanonicalPage);
