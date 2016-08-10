import Ember from 'ember';

import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
  speed: safeComputed('stats.distance', 'stats.duration', (distance, duration) => distance / duration),
  avgDistance: safeComputed('stats.distance', 'stats.flights', (distance, flights) => distance / flights),
  avgDuration: safeComputed('stats.duration', 'stats.flights', (duration, flights) => duration / flights),
});
