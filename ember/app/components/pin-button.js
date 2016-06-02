import Ember from 'ember';

export default Ember.Component.extend({
  classNames: 'btn btn-default',

  didReceiveAttrs() {
    let sfid = this.get('flightId');
    this.set('pinned', isPinnedFlight(sfid));
  },

  click() {
    let sfid = this.get('flightId');

    if (!isPinnedFlight(sfid)) {
      pinFlight(sfid);
      this.set('pinned', true);
    } else {
      unpinFlight(sfid);
      this.set('pinned', false);
    }
  }
});
