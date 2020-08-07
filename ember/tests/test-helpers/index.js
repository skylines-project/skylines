import {
  setupTest as _setupTest,
  setupRenderingTest as _setupRenderingTest,
  setupApplicationTest as _setupApplicationTest,
} from 'ember-qunit';

export function setupTest(hooks, options) {
  _setupTest(hooks, options);
}

export function setupRenderingTest(hooks, options) {
  _setupRenderingTest(hooks, options);
}

export function setupApplicationTest(hooks, options) {
  _setupApplicationTest(hooks, options);
}
