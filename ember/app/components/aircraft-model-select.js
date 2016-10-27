import Ember from 'ember';

export default Ember.Component.extend({
  tagName: '',

  models: [],
  modelId: null,

  modelsWithNull: Ember.computed('models.[]', function() {
    return [{ id: null }].concat(this.get('models'));
  }),

  model: Ember.computed('modelsWithNull.[]', 'modelId', function() {
    return this.get('modelsWithNull').findBy('id', this.get('modelId') || null);
  }),

  actions: {
    onChange(model) {
      this.get('onChange')(model.id);
    },
  },
});
