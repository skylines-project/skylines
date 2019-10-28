import Component from '@ember/component';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  tagName: '',
  speed: safeComputed('stats.distance', 'stats.duration', (distance, duration) => distance / duration),
  avgDistance: safeComputed('stats.distance', 'stats.flights', (distance, flights) => distance / flights),
  avgDuration: safeComputed('stats.duration', 'stats.flights', (duration, flights) => duration / flights),
});
