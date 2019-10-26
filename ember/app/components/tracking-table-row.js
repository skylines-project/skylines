import Component from '@ember/component';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  tagName: '',

  altitudeAGL: safeComputed('track.altitude', 'track.elevation', (altitude, elevation) =>
    Math.max(altitude - elevation, 0),
  ),
});
