import Ember from 'ember';

export default function parseQueryString(qs) {
  if (!qs) {
    return {};
  }

  if (qs[0] === '?') {
    qs = qs.slice(1);
  }

  let RR = Ember.__loader.require('route-recognizer').default;
  let parseQueryString = RR.prototype.parseQueryString;
  return parseQueryString(qs);
}
