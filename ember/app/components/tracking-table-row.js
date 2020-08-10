import Component from '@glimmer/component';

import safeComputed from '../computed/safe-computed';

export default class TrackingTableRow extends Component {
  @safeComputed('track.altitude', 'track.elevation', (altitude, elevation) => Math.max(altitude - elevation, 0))
  altitudeAGL;
}
