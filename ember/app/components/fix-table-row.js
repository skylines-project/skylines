import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { htmlSafe } from '@ember/template';

export default Component.extend({
  tagName: '',
  selectable: false,

  badgeStyle: computed('row.color', function() {
    return htmlSafe(`background-color: ${this.row.color}`);
  }),

  actions: {
    remove() {
      this.onRemove(this.get('row.id'));
    },
  },

  handleClick: action(function() {
    if (this.selectable) {
      this.onSelect(this.get('row.id'));
    }
  }),
});
