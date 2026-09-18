import { setApplication } from '@ember/test-helpers';
import { start } from 'ember-qunit';

import Application from '../app';
import config from '../config/environment';
import registerMatchJsonAssertion from './test-helpers/match-json';

registerMatchJsonAssertion();

setApplication(Application.create(config.APP));

const originalOnerror = window.onerror;
window.onerror = function (msg, url, line, col, error) {
  if (error && error.name === 'TransitionAborted') {
    return true;
  }
  if (typeof msg === 'string' && msg.includes('TransitionAborted')) {
    return true;
  }
  if (originalOnerror) {
    return originalOnerror.apply(this, arguments);
  }
  return false;
};

start();
