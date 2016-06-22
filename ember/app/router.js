import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType,
});

Router.map(function() {
  this.route('club', { path: '/clubs/:club_id' });
  this.route('clubs', { path: '/clubs' });

  this.route('users', { path: '/users' });

  this.route('stats', { path: '/statistics' }, function() {
    this.route('wildcard', { path: '/*wildcard' });
  });

  this.route('flight', { path: '/flights/:flight_id' });

  this.route('flights', { path: '/flights' }, function() {
    this.route('list', { path: '/*wildcard' });
  });

  this.route('tracking', function() {
    this.route('details', { path: '/:user_ids' });
  });

  this.route('ranking', function() {
    this.route('clubs');
    this.route('pilots');
    this.route('airports');
  });

  this.route('search');

  this.route('islands', { path: '/*wildcard' });
});

export default Router;
