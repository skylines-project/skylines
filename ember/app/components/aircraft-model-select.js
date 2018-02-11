import { computed } from '@ember/object';
import Component from '@ember/component';
import { or } from 'ember-awesome-macros';
import { findBy } from 'ember-awesome-macros/array';
import raw from 'ember-macro-helpers/raw';

export default Component.extend({
  tagName: '',

  models: null,
  modelId: null,

  modelsWithNull: computed('models.[]', function() {
    return [{ id: null }].concat(this.get('models'));
  }),

  model: findBy('modelsWithNull', raw('id'), or('modelId', null)),

  actions: {
    onChange(model) {
      this.get('onChange')(model.id);
    },
  },
});
