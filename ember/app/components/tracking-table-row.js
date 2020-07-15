import Component from '@ember/component';

import safeComputed from '../computed/safe-computed';

export default class TrackingTableRow extends Component {
  tagName = '';

  @safeComputed('track.altitude', 'track.elevation', (altitude, elevation) => Math.max(altitude - elevation, 0))
  altitudeAGL;
}
