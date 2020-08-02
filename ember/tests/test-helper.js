import { setApplication } from '@ember/test-helpers';
import { start } from 'ember-qunit';

import Application from '../app';
import config from '../config/environment';
import registerMatchJsonAssertion from './test-helpers/match-json';

registerMatchJsonAssertion();

setApplication(Application.create(config.APP));

start();
