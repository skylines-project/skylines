import Component from '@ember/component';
import { action, computed } from '@ember/object';

export default class extends Component {
  tagName = '';

  nearFlights = null;
  visibleFlights = null;

  @computed('nearFlights.[]', 'visibleFlights.[]')
  get nearFlightsWithColors() {
    let { nearFlights, visibleFlights } = this;
    return nearFlights.map(it => {
      let id = it.flight.id;
      let visibleFlight = visibleFlights.findBy('id', id);

      return {
        color: visibleFlight ? visibleFlight.get('color') : undefined,
        flight: it.flight,
        times: it.times,
      };
    });
  }

  @action
  select(id) {
    this.onSelect(id);
  }
}
