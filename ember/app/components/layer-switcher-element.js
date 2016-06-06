import Ember from 'ember';

export default Ember.Component.extend({
  highlighted: false,

  imagePath: Ember.computed('layer.visible', 'highlighted', function() {
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
