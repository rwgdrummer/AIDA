import axios from 'axios';

export const ROOT_URI = 'http://127.0.0.1:5000/api/v1';

export function getTestAPI() {
  return axios.get(`${ROOT_URI}`);
}

export function getEntitiesList() {
  return axios.get(`${ROOT_URI}/entities_without_canonical`);
}
export function getEntityMentions(entityId) {
  return axios.get(`${ROOT_URI}/entity_mentions?entity_id=${entityId}`);
}
export function getParentChildDetail(provenance) {
  return axios.get(`${ROOT_URI}/mention/${provenance}`);
}
export function getSegments(childFile) {
  return axios.get(`${ROOT_URI}/segments/${childFile}`);
}
export function getMedia(fileId, frameNumber) {
  return axios.get(`${ROOT_URI}/media?file_id=${fileId}&frame_number=${frameNumber}`);
}
export function getCanonicalMentions(childFile) {
  return axios.get(`${ROOT_URI}/media/${childFile}`);
}
export function deleteCanonicalMention(mentionId) {
  return axios.delete(`${ROOT_URI}/canonical_mentions/${mentionId}`);
}
export function postCanonicalMention() {
  return axios.post(`${ROOT_URI}/canonical_mentions`);
}
