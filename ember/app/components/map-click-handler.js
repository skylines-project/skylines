import Component from '@glimmer/component';

import MapClickHandler from '../utils/map-click-handler';

export default class MapClickHandler extends Component {
  constructor() {
    super(...arguments);

    let { map, flights, addFlight } = this.args;

    let handler = MapClickHandler.create({ map, flights, addFlight });
    map.on('click', event => handler.trigger(event));
  }
}
