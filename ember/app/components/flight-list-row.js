import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'tr',
  classNameBindings: ['private:not_published'],
});
