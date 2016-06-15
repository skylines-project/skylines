import Ember from 'ember';

export default Ember.Component.extend({
  cesiumLoader: Ember.inject.service(),

  tagName: '',

  enabled: false,
  loaded: false,

  enabledObserver: Ember.observer('enabled', function() {
    if (this.get('enabled') && !this.get('loaded')) {
      this.get('cesiumLoader').load().then(() => {
        this.set('loaded', true);
      });
    }
  }),
});
