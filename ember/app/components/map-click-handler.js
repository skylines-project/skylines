import Component from '@glimmer/component';

import slMapClickHandler from '../utils/map-click-handler';

export default class MapClickHandler extends Component {
  constructor() {
    super(...arguments);
    slMapClickHandler(this.args.map, this.args.flights, this.args.addFlight);
  }
}
