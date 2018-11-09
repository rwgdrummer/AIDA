import { fromJS } from 'immutable';
import canonicalPageReducer from '../reducer';

describe('canonicalPageReducer', () => {
  it('returns the initial state', () => {
    expect(canonicalPageReducer(undefined, {})).toEqual(fromJS({}));
  });
});
