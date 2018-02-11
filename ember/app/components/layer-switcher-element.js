import { computed } from '@ember/object';
import Component from '@ember/component';

export default Component.extend({
  highlighted: false,

  imagePath: computed('layer.visible', 'highlighted', function() {
    let colorful = this.get('layer.visible') || this.get('highlighted');
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
    this.get('onSelect')(this.get('layer'));
  },
});
