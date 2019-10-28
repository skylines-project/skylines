import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  tagName: '',

  highlighted: false,

  imagePath: computed('layer.visible', 'highlighted', function() {
    let colorful = this.get('layer.visible') || this.highlighted;
    return `../../images/layers/${this.get('layer.name')}${colorful ? '.png' : '.bw.png'}`;
  }),
});
