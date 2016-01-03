var slTaskCollection = Backbone.Collection.extend({
  initialize: function() {
  },

  url: function() {
    return '/tasks/';
  }
});
