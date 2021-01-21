import Component from '@ember/component';
import { computed } from '@ember/object';
import { oneWay, equal } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  files: {
    descriptionKey: 'file-upload-field',
    validators: [validator('presence', true)],
    debounce: 0,
  },
  pilotId: {
    descriptionKey: 'pilot',
    validators: [],
    debounce: 0,
  },
  pilotName: {
    descriptionKey: 'pilot',
    validators: [validator('length', { max: 255 })],
    debounce: 500,
  },
});

export default Component.extend(Validations, {
  tagName: '',

  ajax: service(),
  account: service(),

  clubMembers: null,
  pilotName: null,
  error: null,
  onUpload() {},

  pilotId: oneWay('account.user.id'),

  showPilotNameInput: equal('pilotId', null),

  uploadToWeGlide: false,
  weglideUserId: null,
  weglideBirthday: null,

  weglideBirthdayIsValid: computed('weglideBirthday', function () {
    return /^\d{4}-\d{2}-\d{2}$/.test(this.weglideBirthday);
  }),

  submitDisabled: computed(
    'uploadToWeGlide',
    'weglideUserId',
    'weglideBirthday',
    'uploadTask.isRunning',
    'validations.isValid',
    function () {
      if (this.uploadToWeGlide && (!this.weglideUserId || !this.weglideBirthday)) return true;

      return this.uploadTask.isRunning || !this.validations.isValid;
    },
  ),

  actions: {
    setFilesFromEvent(event) {
      this.set('files', event.target.files);
    },

    async submit(event) {
      event.preventDefault();

      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.uploadTask.perform(event.target);
      }
    },

    toggleWeGlide(event) {
      this.set('uploadToWeGlide', event.target.checked);
    },

    updateWeGlideUserId(userId) {
      this.set('weglideUserId', userId);
    },

    updateWeGlideBirthday(event) {
      this.set('weglideBirthday', event.target.value);
    },
  },

  uploadTask: task(function* (form) {
    let data = new FormData(form);

    try {
      let json = yield this.ajax.request('/api/flights/upload/', {
        method: 'POST',
        data,
        contentType: false,
        processData: false,
      });
      this.onUpload(json);
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
