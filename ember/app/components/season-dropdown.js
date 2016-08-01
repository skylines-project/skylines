import Ember from 'ember';

export default Ember.Component.extend({
  year: null,

  init() {
    this._super(...arguments);

    let year = (new Date()).getFullYear();
    this.set('recentYears', [0, 1, 2, 3, 4].map(i => year - i));
  },
});
