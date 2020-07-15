import Component from '@glimmer/component';

import safeComputed from '../computed/safe-computed';

export default class UserQuickStats extends Component {
  @safeComputed('args.stats.distance', 'args.stats.duration', (distance, duration) => distance / duration) speed;
  @safeComputed('args.stats.distance', 'args.stats.flights', (distance, flights) => distance / flights) avgDistance;
  @safeComputed('args.stats.duration', 'args.stats.flights', (duration, flights) => duration / flights) avgDuration;
}
