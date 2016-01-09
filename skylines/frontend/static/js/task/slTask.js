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
                  'change:coordinate',
                  function(turnpoint) {
          this.updateGeometry();
          this.updateBearings(turnpoint);
        }.bind(this));

    this.listenTo(this.attributes.turnpoints,
                  'remove add',
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

  updateBearings: function(turnpoint) {
    if (this.getLength() < 2) return;

    if (typeof turnpoint == 'number')
      var current = turnpoint;
    else
      var current = this.attributes.turnpoints.indexOf(turnpoint);

    var start = Math.max(0, current - 1);
    var end = Math.min(current + 1, this.getLength() - 1);

    for (var i = start; i <= end; i++)
      this.updateBearing(this.getTurnpointAt(i));
  },

  updateBearing: function(turnpoint) {
    if (turnpoint === this.getFirstTurnpoint()) {
      var this_coordinate = turnpoint.getCoordinate();
      var next_coordinate = this.getTurnpointAt(1).getCoordinate();
      var next_bearing = calculateBearing(this_coordinate,
                                          next_coordinate);

      turnpoint.setBearings(null, next_bearing);
    } else if (turnpoint === this.getLastTurnpoint()) {
      var this_coordinate = turnpoint.getCoordinate();
      var previous_coordinate = this.getTurnpointAt(-2).getCoordinate();
      var previous_bearing = calculateBearing(this_coordinate,
                                              previous_coordinate);

      turnpoint.setBearings(previous_bearing, null);
    } else {
      var this_coordinate = turnpoint.getCoordinate();
      var index = this.attributes.turnpoints.indexOf(turnpoint);

      var previous_coordinate = this.getTurnpointAt(index - 1).getCoordinate();
      var previous_bearing = calculateBearing(this_coordinate,
                                              previous_coordinate);

      var next_coordinate = this.getTurnpointAt(index + 1).getCoordinate();
      var next_bearing = calculateBearing(this_coordinate,
                                          next_coordinate);

      turnpoint.setBearings(previous_bearing, next_bearing);
    }
  },

  getTurnpointAt: function(index) {
    return this.attributes.turnpoints.at(index);
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

    // Proxy change:type event to the outside
    this.listenTo(turnpoint, 'change:type', function(turnpoint) {
      this.trigger('change:turnpoint:type', this, turnpoint);
    }.bind(this));

    // Update bearings for this and the surrounding turnpoints
    this.updateBearings(turnpoint);

    return turnpoint;
  },

  getFirstTurnpoint: function() {
    return this.attributes.turnpoints.first();
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
      var position = this.attributes.turnpoints.indexOf(turnpoint);
      this.trigger('remove:turnpoint', this, turnpoint);
      turnpoint.destroy();

      this.updateBearings(position);
      return true;
    } else {
      return false;
    }
  },

  removeLastTurnpoint: function() {
    return this.removeTurnpoint(this.getLastTurnpoint());
  }
});


function calculateBearing(c0, c1) {
  // Are the points coincident?
  if (c0[0] == c1[0] && c0[1] == c1[1])
    return 0;

  c0 = ol.proj.toLonLat(c0);
  c1 = ol.proj.toLonLat(c1);

  c0[0] = c0[0] / 180 * Math.PI;
  c0[1] = c0[1] / 180 * Math.PI;
  c1[0] = c1[0] / 180 * Math.PI;
  c1[1] = c1[1] / 180 * Math.PI;

  var bearing = 0;
  var adjust = 0;

  var a = Math.cos(c1[1]) * Math.sin(c1[0] - c0[0]);
  var b = Math.cos(c0[1]) * Math.sin(c1[1]) -
          Math.sin(c0[1]) * Math.cos(c1[1]) * Math.cos(c1[0] - c0[0]);

  if ((a == 0) && (b == 0)) {
    bearing = 0;
  } else if (b == 0) {
    if (a < 0)
      bearing = 3 * Math.PI / 2;
    else
      bearing = Math.PI / 2;
  } else if (b < 0) {
    adjust = Math.PI;
  } else {
    if (a < 0)
      adjust = 2 * Math.PI;
    else
      adjust = 0;
  }

  bearing = (Math.atan(a / b) + adjust) * 180 / Math.PI;
  return bearing;
}
