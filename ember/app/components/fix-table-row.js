import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'tr',
  classNameBindings: ['selected', 'selectable'],

  badgeStyle: Ember.computed('row.color', function() {
    return Ember.String.htmlSafe(`background-color: ${this.get('row.color')}`);
  }),

  click() {
    this.get('onSelect')(this.get('row.id'));
  },

  actions: {
    remove() {
      this.get('onRemove')(this.get('row.id'));
    },
  },
});
