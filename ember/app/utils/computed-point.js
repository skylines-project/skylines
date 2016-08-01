import ol from 'openlayers';

import safeComputed from './safe-computed';

export default function computedPoint(key, layout = 'XYZM') {
  return safeComputed(key, coordinate => {
    if (layout === 'XY') {
      coordinate = coordinate.slice(0, 2);
    }

    return new ol.geom.Point(coordinate, layout);
  });
}
