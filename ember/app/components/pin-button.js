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

/**
 * Checks if the flight id is a pinned flight
 *
 * @param {Number} sfid SkyLines flight ID.
 * @return {Boolean} True if the flight is pinned.
 */
function isPinnedFlight(sfid) {
  var pinnedFlights = getPinnedFlights();

  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] == sfid) return true;
  }

  return false;
}
