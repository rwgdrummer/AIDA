/*
 *
 * CanonicalPage actions
 *
 */

import {
  DEFAULT_ACTION,
  GET_ENTITIES,
  GET_ENTITIES_SUCCESS,
  GET_ENTITIES_FAILURE,
  GET_ENTITY_MENTIONS,
  GET_ENTITY_MENTIONS_SUCCESS,
  GET_ENTITY_MENTIONS_FAILURE,
  POST_CANONICAL_MENTION,
  POST_CANONICAL_MENTION_SUCCESS,
  POST_CANONICAL_MENTION_FAILURE,
  DELETE_CANONICAL_MENTION,
  DELETE_CANONICAL_MENTION_SUCCESS,
  DELETE_CANONICAL_MENTION_FAILURE,
  GET_TEST,
  GET_TEST_SUCCESS,
  GET_TEST_FAILURE,

} from './constants';

export function getTest() {
  console.log("Action getTest method");
  return {
    type: GET_TEST
  };
}

export function getTestSuccess(data) {
  console.log("Action getTest Success Method");
  return {
    type: GET_TEST_SUCCESS,
    data
  };
}

export function getTestFailure(error) {
  console.log("Action getTestFailure method");
  return {
    type: GET_TEST_FAILURE,
    error
  };
}





export function getEntities() {
  return {
    type: GET_ENTITIES,
  };
}

export function getEntitiesSuccess(entities) {
  return {
    type: GET_ENTITIES_SUCCESS,
    entities
  };
}

export function getEntitiesFailure(error) {
  return {
    type: GET_ENTITIES_FAILURE,
    error
  };
}

export function getEntityMentions(entityId) {
  return {
    type: GET_ENTITY_MENTIONS,
    entityId
  };
}

export function getEntityMentionsSuccess(entityMention) {
  return {
    type: GET_ENTITY_MENTIONS_SUCCESS,
    entityMention
  };
}

export function getEntityMentionsFailure(error) {
  return {
    type: GET_ENTITY_MENTIONS_FAILURE,
    error
  };
}

export function postCanonicalMention() {
  return {
    type: POST_CANONICAL_MENTION,
  };
}

export function postCanonicalMentionSuccess(success) {
  return {
    type: POST_CANONICAL_MENTION_SUCCESS,
    success
  };
}

export function postCanonicalMentionFailure(error) {
  return {
    type: POST_CANONICAL_MENTION_FAILURE,
    error
  };
}

export function deleteCanonical(canonicalId) {
  return {
    type: DELETE_CANONICAL_MENTION,
    canonicalId
  };
}

export function deleteCanonicalSuccess(success) {
  return {
    type: DELETE_CANONICAL_MENTION_SUCCESS,
    success
  };
}

export function deleteCanonicalFailure(error) {
  return {
    type: DELETE_CANONICAL_MENTION_FAILURE,
    error
  };
}

export function defaultAction() {
  return {
    type: DEFAULT_ACTION,
  };
}

