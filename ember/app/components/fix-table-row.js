import Component from '@ember/component';
import { tag } from 'ember-awesome-macros';
import { htmlSafe } from 'ember-awesome-macros/string';

export default Component.extend({
  tagName: 'tr',
  classNameBindings: ['selected', 'selectable'],

  selectable: false,

  badgeStyle: htmlSafe(tag`background-color: ${'row.color'}`),

  actions: {
    remove() {
      this.get('onRemove')(this.get('row.id'));
    },
  },

  click() {
    if (this.get('selectable')) {
      this.get('onSelect')(this.get('row.id'));
    }
  },
});
