import EmberRouter from '@ember/routing/router';

import config from './config/environment';

const Router = EmberRouter.extend({
  location: config.locationType,
  rootURL: config.rootURL,
});

Router.map(function() {

  this.route('testgroupflight',{ path: '/testgroupflight/:groupflight_id' });
//  this.route('testgroupflight');
  this.route('club', { path: '/clubs/:club_id' }, function() {
    this.route('pilots');
    this.route('edit');
  });

  this.route('clubs');

  this.route('user', { path: '/users/:user_id' }, function() {
    this.route('followers');
    this.route('following');
  });

  this.route('users', { path: '/users' }, function() {
    this.route('new');
    this.route('recover');
  });

  this.route('statistics', { path: '/statistics' }, function() {
    this.route('airport', { path: '/airport/:airport_id' });
    this.route('club', { path: '/club/:club_id' });
    this.route('pilot', { path: '/pilot/:pilot_id' });
  });

  this.route('flight-upload', { path: '/flights/upload' });
//note: the route (template, other files are named 'flight, but the path of the routs is flights.  Why _ids?
  this.route('flight', { path: '/flights/:flight_ids' }, function() {
    this.route('change-aircraft', { path: '/change_aircraft' });
    this.route('change-pilot', { path: '/change_pilot' });
    this.route('map-redirect', { path: '/map' });
  });

  this.route('flights', { path: '/flights' }, function() {
    this.route('all');
    this.route('latest');
    this.route('date', { path: '/date/:date' });
    this.route('landscape', { path: '/landscape/:landscape' });
    this.route('airport', { path: '/airport/:airport_id' });
    this.route('club', { path: '/club/:club_id' });
    this.route('pilot', { path: '/pilot/:pilot_id' });
    this.route('unassigned');
    this.route('pinned');
    this.route('list', { path: '/list/:list' });
  });

//  this.route('groupflight', { path: '/groupflights/:groupflight_ids' });
   this.route('groupflight', { path: '/groupflights/:groupflight_id' });

  this.route('groupflights', { path: '/groupflights' }, function() {
    this.route('all');
    this.route('latest');
    this.route('date', { path: '/date/:date' });
    this.route('landscape', { path: '/landscape/:landscape' });
    this.route('airport', { path: '/airport/:airport_id' });
    this.route('club', { path: '/club/:club_id' });
    this.route('pinned');
    this.route('list', { path: '/list/:list' });
  });

  this.route('tracking', function() {
    this.route('info');
    this.route('details', { path: '/:user_ids' });
    this.route('map-redirect', { path: '/:user_ids/map' });
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

  this.route('about', function() {
    this.route('imprint');
    this.route('license');
    this.route('team');
  });

  this.route('login');

  this.route('freestyle');

  this.route('page-not-found', { path: '/*wildcard' });
});

export default Router;
