var slTask = Backbone.Model.extend({
  idAttribute: 'task_id',

  defaults: function() {
    return {
      task_id: null,
      turnpoints: new Backbone.Collection(),
      geometry: new ol.geom.LineString([], 'XYM')
    };
  },

  initialize: function() {
    this.listenTo(this.attributes.turnpoints,
                  'change:coordinate remove add',
                  function(turnpoint) {
          this.updateGeometry();
        }.bind(this));
  },

  updateGeometry: function() {
    var coords = [];

    this.attributes.turnpoints.each(function(turnpoint, index) {
      coords.push(turnpoint.getCoordinate().concat(index));
    });

    this.attributes.geometry.setCoordinates(coords);
  },

  getGeometry: function() {
    return this.attributes.geometry;
  },

  getID: function() {
    return this.attributes.task_id;
  },

  addTurnpoint: function(coordinate, position) {
    var turnpoint = new slTurnpoint({
      coordinate: coordinate
    });

    if (position) {
      this.attributes.turnpoints.add(turnpoint, {at: position});
    } else {
      this.attributes.turnpoints.add(turnpoint);
    }
    this.trigger('add:turnpoint', this, turnpoint);

    return turnpoint;
  },

  getLastTurnpoint: function() {
    return this.attributes.turnpoints.last();
  },

  getPreviousTurnpoint: function() {
    return this.attributes.turnpoints.at(-2);
  },

  getLength: function() {
    return this.attributes.turnpoints.length;
  },

  getTurnpoints: function() {
    return this.attributes.turnpoints;
  },

  removeTurnpoint: function(turnpoint) {
    if (this.getLength() > 2) {
      this.trigger('remove:turnpoint', this, turnpoint);
      turnpoint.destroy();
      return true;
    } else {
      return false;
    }
  },

  removeLastTurnpoint: function() {
    return this.removeTurnpoint(this.getLastTurnpoint());
  }
});
