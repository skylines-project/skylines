import Ember from 'ember';

export default Ember.Component.extend({
  fixCalc: Ember.inject.service(),
  pinnedFlights: Ember.inject.service(),

  classNames: ['olFullscreen'],

  didInsertElement() {
    let sidebar = this.$('#sidebar').sidebar();

    this.$('#barogram_panel').resize(() => {
      let height = this.$('#barogram_panel').height() + 10;
      sidebar.css('bottom', height);
      this.$('.ol-scale-line').css('bottom', height);
      this.$('.ol-attribution').css('bottom', height);
    });

    if (window.location.hash &&
      sidebar.find(`li > a[href="#${window.location.hash.substring(1)}"]`).length != 0) {
      sidebar.open(window.location.hash.substring(1));
    }

    window.paddingFn = () => [20, 20, this.$('#barogram_panel').height() + 20, sidebar.width() + 20];
  },

  actions: {
    selectWingman(id) {
      let fixCalc = this.get('fixCalc');
      let pinnedFlights = this.get('pinnedFlights');

      let flights = fixCalc.get('flights');
      let matches = flights.filterBy('id', id);
      if (matches.length !== 0) {
        flights.removeObjects(matches);
        pinnedFlights.unpin(id);
      } else {
        fixCalc.addFlightFromJSON(`/flights/${id}/json`);
        pinnedFlights.pin(id);
      }
    },
  },
});
