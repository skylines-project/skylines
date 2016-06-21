import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType,
});

Router.map(function() {
  this.route('stats', { path: '/statistics' }, function() {
    this.route('wildcard', { path: '/*wildcard' });
  });

  this.route('islands', { path: '/*wildcard' });
});

export default Router;
