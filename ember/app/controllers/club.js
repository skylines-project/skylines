import Ember from 'ember';

export default Ember.Controller.extend({
  club: Ember.computed.readOnly('model'),
});
