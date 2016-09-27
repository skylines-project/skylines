import Ember from 'ember';

import BaseMapComponent from './base-map';
import slMapClickHandler from '../utils/map-click-handler';
import slMapHoverHandler from '../utils/map-hover-handler';

export default BaseMapComponent.extend({
  fixCalc: Ember.inject.service(),

  flights: Ember.computed.readOnly('fixCalc.flights'),

  didInsertElement() {
    this._super(...arguments);
    this.get('map').on('moveend', this._handleMoveEnd, this);

    let fixCalc = this.get('fixCalc');

    slMapHoverHandler.create({
      fixCalc,
      flightMap: this,
    });

    slMapClickHandler(this.get('map'), fixCalc.get('flights'));
  },

  willDestroyElement() {
    this._super(...arguments);
    this.get('map').off('moveend', this._handleMoveEnd, this);
  },

  _handleMoveEnd(event) {
    this.getWithDefault('onExtentChange', Ember.K)(event.frameState.extent);
  },

  actions: {
    cesiumEnabled() {
      this.set('cesiumEnabled', true);
      this.getWithDefault('onCesiumEnabledChange', Ember.K)(true);
    },
    cesiumDisabled() {
      this.set('cesiumEnabled', false);
      this.getWithDefault('onCesiumEnabledChange', Ember.K)(false);
    },
  },
});
