import Ember from 'ember';

export default Ember.Controller.extend({
  queryParams: ['text'],

  searchText: Ember.computed.readOnly('text'),
  searchTextInput: Ember.computed.oneWay('searchText'),

  results: Ember.computed.readOnly('model.results'),

  actions: {
    search(text) {
      this.transitionToRoute({ queryParams: { text }})
    },
  },
});
