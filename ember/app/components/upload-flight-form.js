import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  files: {
    descriptionKey: 'file-upload-field',
    validators: [
      validator('presence', true),
    ],
    debounce: 0,
  },
  pilotId: {
    descriptionKey: 'pilot',
    validators: [],
    debounce: 0,
  },
  pilotName: {
    descriptionKey: 'pilot',
    validators: [
      validator('length', { max: 255 }),
    ],
    debounce: 500,
  },
});

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  classNames: ['panel-body'],

  clubMembers: [],

  pilotId: Ember.computed.oneWay('account.user.id'),
  pilotName: null,

  pending: false,
  error: null,

  showPilotNameInput: Ember.computed.equal('pilotId', null),

  didInsertElement() {
    this.$('iframe').on('load', this.onIframeLoad.bind(this));
  },

  willDestroyElement() {
    this.$('iframe').off('load');
  },

  onIframeLoad() {
    let text = this.$('iframe').contents().text();
    if (Ember.isBlank(text)) return;

    this.set('pending', false);

    let json = JSON.parse(text);

    if (json.error) {
      this.set('error', json.error);
    } else {
      this.getWithDefault('onUpload', Ember.K)(json);
    }
  },

  submitForm() {
    this.set('pending', true);
    this.$('form')[0].submit();
  },

  actions: {
    setFilesFromEvent(event) {
      this.set('files', event.target.value);
    },

    submit() {
      // start async validations
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          // if validation passed continue submitting the form
          this.submitForm();
        }
      });

      // prevent form from submitting synchronously
      return false;
    },
  },
});
