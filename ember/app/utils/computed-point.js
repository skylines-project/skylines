import Ember from 'ember';
import ol from 'openlayers';

export default function computedPoint(key, layout = 'XYZM') {
  return Ember.computed(key, function() {
    let coordinate = this.get(key);
    if (coordinate) {
      if (layout === 'XY') {
        coordinate = coordinate.slice(0, 2);
      }

      return new ol.geom.Point(coordinate, layout);
    }
  })
}
