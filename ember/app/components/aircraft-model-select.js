import Ember from 'ember';
import { or } from 'ember-awesome-macros';
import { findBy } from 'ember-awesome-macros/array';
import raw from 'ember-macro-helpers/raw';

export default Ember.Component.extend({
  tagName: '',

  models: [],
  modelId: null,

  modelsWithNull: Ember.computed('models.[]', function() {
    return [{ id: null }].concat(this.get('models'));
  }),

  model: findBy('modelsWithNull', raw('id'), or('modelId', null)),

  actions: {
    onChange(model) {
      this.get('onChange')(model.id);
    },
  },
});
