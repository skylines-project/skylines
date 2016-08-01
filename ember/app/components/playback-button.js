import Ember from 'ember';

export default Ember.Component.extend({
  fixCalc: Ember.inject.service(),

  classNames: ['PlayButton', 'ol-unselectable'],

  click() {
    this.toggle();
  },

  touchEnd() {
    this.toggle();
  },

  toggle() {
    let service = this.get('fixCalc');
    if (service.get('isRunning')) {
      service.stopPlayback();
    } else {
      service.startPlayback();
    }
  },
});
