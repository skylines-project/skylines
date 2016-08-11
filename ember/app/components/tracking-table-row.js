import Ember from 'ember';

import safeComputed from '../computed/safe-computed';

export default Ember.Component.extend({
  tagName: 'tr',

  altitudeAGL: safeComputed('track.altitude', 'track.elevation',
    (altitude, elevation) => Math.max(altitude - elevation, 0)),
});
