import RSVP from 'rsvp';

export function initialize() {
  window.Promise = RSVP.Promise;
}

export default {
  name: 'promise-polyfill',
  initialize,
};
