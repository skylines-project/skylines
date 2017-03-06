import Ember from 'ember';
import { tag } from 'ember-awesome-macros';
import { htmlSafe } from 'ember-awesome-macros/string';

export default Ember.Component.extend({
  tagName: 'tr',
  classNameBindings: ['selected', 'selectable'],

  selectable: false,

  badgeStyle: htmlSafe(tag`background-color: ${'row.color'}`),

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
