import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  tagName: '',

  models: null,
  modelId: null,

  modelsWithNull: computed('models.[]', function() {
    return [{ id: null }].concat(this.models);
  }),

  model: computed('modelsWithNull.@each.id', 'modelId', function() {
    return this.modelsWithNull.findBy('id', this.modelId || null);
  }),

  actions: {
    onChange(model) {
      this.onChange(model.id);
    },
  },
});
