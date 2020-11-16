import Point from 'ol/geom/Point';

import safeComputed from './safe-computed';

export default function computedPoint(key, layout = 'XYZM') {
  return safeComputed(key, coordinate => {
    if (layout === 'XY') {
      coordinate = coordinate.slice(0, 2);
    }

    return new Point(coordinate, layout);
  });
}
