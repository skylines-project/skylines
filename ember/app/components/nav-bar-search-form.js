import Ember from 'ember';

export default Ember.Component.extend({
  searchTextService: Ember.inject.service('searchText'),

  tagName: 'form',
  attributeBindings: ['action'],
  classNames: ['navbar-form', 'navbar-left', 'navbar-search', 'visible-lg'],
  action: '/search/',
});
