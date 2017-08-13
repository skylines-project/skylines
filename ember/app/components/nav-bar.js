import Ember from 'ember';

export default Ember.Component.extend({
  tagName: '',

  collapsed: true,

  actions: {
    didClickUpload() {
      this.set('collapse', true);
      this.didClickUpload();
    },
  },
});
