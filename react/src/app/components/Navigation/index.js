/**
 *
 * Navigation
 *
 */

import React from "react";
import { Button } from 'semantic-ui-react';

// import PropTypes from 'prop-types';
// import styled from 'styled-components';

/* eslint-disable react/prefer-stateless-function */
class Navigation extends React.Component {
  render() {
    return (
      <div>
        <Button>Add</Button>
        <Button>Prev</Button>
        <Button>Next</Button>
      </ div>
    );
  }
}

Navigation.propTypes = {};

export default Navigation;
