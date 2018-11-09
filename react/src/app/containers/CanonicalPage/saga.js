// import { take, call, put, select } from 'redux-saga/effects';
import { takeLatest, call, put } from 'redux-saga/effects';
import { push } from 'react-router-redux';
import { getEntitiesList, deleteCanonicalMention, getTestAPI } from '../../api';
import { getEntitiesSuccess, deleteCanonicalSuccess, getTestSuccess, getTest } from './actions';
import { GET_ENTITIES, DELETE_CANONICAL_MENTION, GET_TEST } from './constants';

//gets the list of entities without a canonical
function* getTestSaga() {
  try {
    console.log("Attempted API call")
    const { data } = yield call(getTestAPI);
    yield put(getTestSuccess(data));
    console.log('Successful api call');
  } catch (e) {
    console.log(e);
  }
}

function* getEntitiesSaga() {
  try {
    const { data } = yield call(getEntitiesList);
    yield put(getEntitiesSuccess(data));
  } catch (e) {
    console.log(e);
  }
}

function* deleteCanonicalSaga(action) {
  try {
    const { data } = yield call(deleteCanoncialMention, action.canonicalId);
    yield put(deleteCanonicalSuccess(data));
  } catch (e) {
    console.log(e);
  }
}


// Individual exports for testing
export default function* defaultSaga() {
  yield [
    takeLatest(GET_ENTITIES, getEntitiesSaga),
    takeLatest(GET_TEST, getTestSaga),
    takeLatest(DELETE_CANONICAL_MENTION, deleteCanonicalSaga),

  ]
}

