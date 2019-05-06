import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  highlighted: false,

  imagePath: computed('layer.visible', 'highlighted', function() {
    let colorful = this.get('layer.visible') || this.highlighted;
    return `../../images/layers/${this.get('layer.name')}${colorful ? '.png' : '.bw.png'}`;
  }),

  mouseEnter() {
    this.set('highlighted', true);
  },
  mouseLeave() {
    this.set('highlighted', false);
  },
  touchStart() {
    this.set('highlighted', true);
  },
  touchEnd() {
    this.set('highlighted', false);
  },

  click() {
    this.onSelect(this.layer);
  },
});
