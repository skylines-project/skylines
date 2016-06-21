import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType,
});

Router.map(function() {
  this.route('stats', { path: '/statistics' }, function() {
    this.route('wildcard', { path: '/*wildcard' });
  });

  this.route('flight', { path: '/flights/:flight_id' });

  this.route('flights', { path: '/flights' }, function() {
    this.route('list', { path: '/*wildcard' });
  });

  this.route('islands', { path: '/*wildcard' });
});

export default Router;
