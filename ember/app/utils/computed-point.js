import Ember from 'ember';
import ol from 'openlayers';

export default function computedPoint(key) {
  return Ember.computed(key, function() {
    let coordinate = this.get(key);
    if (coordinate) {
      return new ol.geom.Point(coordinate);
    }
  })
}
