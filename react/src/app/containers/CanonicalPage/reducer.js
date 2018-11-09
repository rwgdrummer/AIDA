/*
 *
 * CanonicalPage reducer
 *
 */

import { fromJS } from 'immutable';
import { GET_TEST_SUCCESS } from './constants';

export const initialState = fromJS({
  data: {
    hello: "aida users local"
  }
});

function canonicalPageReducer(state = initialState, action) {
  switch (action.type) {
    case GET_TEST_SUCCESS:
      console.log("Reducers GET_TEST_SUCCESS");
      return state.set('data', fromJS(action.data));
    default:
      console.log("Reducers default");
      return state;
  }
}

export default canonicalPageReducer;
