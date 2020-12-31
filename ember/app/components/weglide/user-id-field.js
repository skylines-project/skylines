import { action } from '@ember/object';
import { guidFor } from '@ember/object/internals';
import { inject as service } from '@ember/service';
import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

import { task, timeout } from 'ember-concurrency';

import config from 'skylines/config/environment';

const LOAD_USER_DEBOUNCE_MS = config.environment === 'test' ? 0 : 150;

export default class UserIdField extends Component {
  @service ajax;

  elementId = guidFor(this);
  @tracked userId = this.args.initialValue;

  config = config;

  constructor() {
    super(...arguments);
    this.loadUser();
  }

  get isValid() {
    return isValid(this.userId);
  }

  get userName() {
    if (String(this.loadUserTask.lastSuccessful?.value?.id) === this.userId) {
      return this.loadUserTask.lastSuccessful.value.name;
    }
  }

  @action onInput(event) {
    this.setUserId(event.target.value);
  }

  setUserId(userId) {
    if (this.userId !== userId) {
      this.userId = userId;
      this.loadUser();
      this.args.onChange?.(this.isValid ? userId : null);
    }
  }

  loadUser() {
    this.loadUserTask.perform(this.userId).catch(() => {
      // Ignore errors because they will be handled in the template
    });
  }

  @(task(function* (userId) {
    // debounce for 350ms
    yield timeout(LOAD_USER_DEBOUNCE_MS);

    if (isValid(userId)) {
      let url = `${config.WeGlide.api}/v1/user/${userId}`;
      return yield this.ajax.request(url);
    }
  }).restartable())
  loadUserTask;
}

function isValid(userId) {
  return /^\d+$/.test(userId);
}
