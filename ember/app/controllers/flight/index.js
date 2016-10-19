import Ember from 'ember';

export default Ember.Controller.extend({
  queryParams: ['baselayer', 'overlays'],
  baselayer: null,
  overlays: null,
});
