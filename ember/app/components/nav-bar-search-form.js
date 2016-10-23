import Ember from 'ember';

export default Ember.Component.extend({
  searchTextService: Ember.inject.service('searchText'),
});
