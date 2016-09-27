import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'tr',
  classNameBindings: ['selected', 'selectable'],

  selectable: false,

  badgeStyle: Ember.computed('row.color', function() {
    return Ember.String.htmlSafe(`background-color: ${this.get('row.color')}`);
  }),

  click() {
    if (this.get('selectable')) {
      this.get('onSelect')(this.get('row.id'));
    }
  },

  actions: {
    remove() {
      this.get('onRemove')(this.get('row.id'));
    },
  },
});
