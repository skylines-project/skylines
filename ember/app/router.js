import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType,
});

Router.map(function() {
  this.route('club', { path: '/clubs/:club_id' }, function() {
    this.route('pilots');
    this.route('edit');
  });
  this.route('clubs', { path: '/clubs' });

  this.route('users', { path: '/users' }, function() {
    this.route('new');
  });

  this.route('stats', { path: '/statistics' }, function() {
    this.route('wildcard', { path: '/*wildcard' });
  });

  this.route('flight-upload', { path: '/flights/upload' });

  this.route('flight', { path: '/flights/:flight_ids' }, function() {
    this.route('change-aircraft', { path: '/change_aircraft' });
    this.route('change-pilot', { path: '/change_pilot' });
  });

  this.route('flights', { path: '/flights' }, function() {
    this.route('all');
    this.route('latest');
    this.route('date', { path: '/date/:date' });
    this.route('airport', { path: '/airport/:airport_id' });
    this.route('club', { path: '/club/:club_id' });
    this.route('pilot', { path: '/pilot/:pilot_id' });
    this.route('unassigned');
    this.route('pinned');
    this.route('list', { path: '/list/:list' });
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

  this.route('timeline');
  this.route('notifications');

  this.route('settings', function() {
    this.route('profile');
    this.route('password');
    this.route('club');
    this.route('tracking');
  });

  this.route('islands', { path: '/*wildcard' });
});

export default Router;
