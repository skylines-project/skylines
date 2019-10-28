import Component from '@ember/component';
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

  actions: {
    setFilesFromEvent(event) {
      this.set('files', event.target.value);
    },

    async submit(event) {
      event.preventDefault();

      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.uploadTask.perform(event.target);
      }
    },
  },

  uploadTask: task(function*(form) {
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
