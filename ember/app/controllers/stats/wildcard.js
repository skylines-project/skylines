import Ember from 'ember';

export default Ember.Controller.extend({
  account: Ember.inject.service(),

  name: Ember.computed.readOnly('model.name'),
  years: Ember.computed.readOnly('model.years'),
  sumPilots: Ember.computed.readOnly('model.sumPilots'),
});
