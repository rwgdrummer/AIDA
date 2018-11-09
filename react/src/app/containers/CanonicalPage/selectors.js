import { createSelector } from 'reselect';
import { initialState } from './reducer';

/**
 * Direct selector to the canonicalPage state domain
 */

const selectCanonicalPageDomain = state =>
  state.get('canonicalPage', initialState);

/**
 * Other specific selectors
 */

/**
 * Default selector used by CanonicalPage
 */

const makeSelectCanonicalPage = () =>
  createSelector(selectCanonicalPageDomain, substate => substate.toJS());

export default makeSelectCanonicalPage;
export { selectCanonicalPageDomain };
