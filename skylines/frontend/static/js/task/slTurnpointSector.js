slTurnpointSector = function(coordinate, heading, _type, opt_options) {
  var options = opt_options || {};
  var sector = {};

  /**
   * Available sector types
   */
  var types = {
    daec: {
      name: 'DAeC keyhole',
      radius: false,
      radius_def: 10000,
      inner_radius: false,
      inner_radius_def: 500,
      render: createKeyholeSector
    },
    fai: {
      name: 'FAI quadrant',
      radius: false,
      radius_def: 10000,
      start_radial: false,
      start_radial_def: -45,
      end_radial: false,
      end_radial_def: 45,
      render: createSector
    },
    faistart: {
      name: 'FAI start quadrant',
      radius: false,
      radius_def: 1000,
      start_radial: false,
      start_radial_def: -45,
      end_radial: false,
      end_radial_def: 45,
      render: createSector
    },
    faifinish: {
      name: 'FAI finish quadrant',
      radius: false,
      radius_def: 1000,
      start_radial: false,
      start_radial_def: -45,
      end_radial: false,
      end_radial_def: 45,
      render: createLine
    },
    circle: {
      name: 'Circle',
      radius: true,
      radius_def: 10000,
      render: createSector
    },
    startline: {
      name: 'Start line',
      radius: true,
      radius_def: 10000,
      render: createLine
    },
    finishline: {
      name: 'Finish line',
      radius: true,
      radius_def: 500,
      render: createLine
    },
    sector: {
      name: 'Sector',
      radius: true,
      radius_def: 10000,
      inner_radius: true,
      inner_radius_def: 3000,
      start_radial: true,
      start_radial_def: 40,
      end_radial: true,
      end_radial_def: 300,
      norotate: true,
      render: createSector
    },
    bgafixedcourse: {
      name: 'BGA Fixed Course',
      radius: false,
      radius_def: 20000,
      inner_radius: false,
      inner_radius_def: 500,
      render: createKeyholeSector
    },
    bgaenhancedoption: {
      name: 'BGA Enh. Opt. Fixed Course',
      radius: false,
      radius_def: 10000,
      render: createBGAEnhancedOptionSector
    },
    bgastartsector: {
      name: 'BGA Start Sector',
      radius: false,
      radius_def: 5000,
      render: createBGAEnhancedOptionSector
    }
  };

  /**
   * Sector type
   * @type {String}
   */
  var type;

  /**
   * Outer radius
   * @type {Number}
   */
  var outer_radius;

  /**
   * Innter radius
   * @type {Number}
   */
  var inner_radius;

  /**
   * Start radial
   * @type {Number}
   */
  var start_radial;

  /**
   * End radial
   * @type {Number}
   */
  var end_radial;

  var sphere = new ol.Sphere(6378137);

  var geometry;

  sector.init = function() {
    this.setType(coordinate, heading, _type, options);
  };

  sector.setType = function(coordinate, heading, sector_type, sector_options) {
    type = sector_type;

    outer_radius = sector_options.outer_radius ||
                   types[type].radius_def;
    inner_radius = sector_options.inner_radius ||
                   types[type].inner_radius_def ||
                   0;
    start_radial = sector_options.start_radial ||
                   types[type].start_radial_def ||
                   0;
    end_radial = sector_options.end_radial ||
                 types[type].end_radial_def ||
                 0;

    types[type].render(coordinate, heading, false);
  };

  sector.getName = function() {
    return types[type].name;
  };

  sector.getType = function() {
    return type;
  };

  sector.getProperties = function() {
    var props = {};

    if (types[type].radius)
        props['radius'] = outer_radius;

    if (types[type].inner_radius)
        props['inner_radius'] = inner_radius;

    if (types[type].start_radial)
        props['start_radial'] = start_radial;

    if (types[type].end_radial)
        props['end_radial'] = end_radial;

    return props;
  };

  sector.highlight = function(state) {
    sector.trigger('change:highlight', state);
  },

  sector.getGeometry = function() {
    return geometry;
  };

  sector.updateGeometry = function(coordinate, heading) {
    types[type].render(coordinate, heading, true);
  };

  sector.toJSON = function() {
    return type;
  };

  function createLine(origin, heading, update) {
    var points = [];

    origin = ol.proj.toLonLat(origin);

    var point = sphere.offset(origin,
                              outer_radius,
                              (-90 + heading) / 180 * Math.PI);
    points.push(ol.proj.fromLonLat(point));

    points.push(ol.proj.fromLonLat(origin));

    point = sphere.offset(origin, outer_radius, (90 + heading) / 180 * Math.PI);
    points.push(ol.proj.fromLonLat(point));

    if (update)
      geometry.setCoordinates(points);
    else
      geometry = new ol.geom.LineString(points);
  };

  function createBGAEnhancedOptionSector(origin, heading, update) {
    var points = [];

    var sides = 48;
    var angle;

    origin = ol.proj.toLonLat(origin);

    for (var i = 0; i < sides; i++) {
      angle = (i * 360 / sides) - 90;
      if (angle >= -90 && angle <= 90) {
        var point = sphere.offset(origin,
                                  outer_radius,
                                  (angle + heading) / 180 * Math.PI);
        points.push(ol.proj.fromLonLat(point));
      } else {
        var point = sphere.offset(origin,
                                  inner_radius,
                                  (angle + heading) / 180 * Math.PI);
        points.push(ol.proj.fromLonLat(point));
      }
    }

    if (update)
      geometry.setCoordinates([points]);
    else
      geometry = new ol.geom.Polygon([points]);
  };

  function createKeyholeSector(origin, heading, update) {
    var points = [];

    var sides = 48;
    var angle;

    origin = ol.proj.toLonLat(origin);

    for (var i = 0; i < sides; i++) {
      angle = (i * 360 / sides) - 45;
      if (angle >= -45 && angle <= 45) {
        var point = sphere.offset(origin,
                                  outer_radius,
                                  (angle + heading) / 180 * Math.PI);
        points.push(ol.proj.fromLonLat(point));
      } else {
        var point = sphere.offset(origin,
                                  inner_radius,
                                  (angle + heading) / 180 * Math.PI);
        points.push(ol.proj.fromLonLat(point));
      }
    }

    if (update)
      geometry.setCoordinates([points]);
    else
      geometry = new ol.geom.Polygon([points]);
  };

  function createSector(origin, heading, update) {
    var sides = 48;

    origin = ol.proj.toLonLat(origin);

    if ((end_radial - start_radial) % 360 == 0) {
      var outer_points = [];

      for (var i = 0; i < sides; i++) {
        var angle = i * 360 / sides;
        var point = sphere.offset(origin,
                                  outer_radius,
                                  (angle + heading) / 180 * Math.PI);
        outer_points.push(ol.proj.fromLonLat(point));
      }

      var inner_points = [];
      if (inner_radius > 0) {
        for (var i = 0; i < sides; i++) {
          var angle = i * 360 / sides;
          var point = sphere.offset(origin,
                                    inner_radius,
                                    (angle + heading) / 180 * Math.PI);
          inner_points.push(ol.proj.fromLonLat(point));
        }
      }

      if (update)
        geometry.setCoordinates([outer_points, inner_points]);
      else
        geometry = new ol.geom.Polygon([outer_points, inner_points]);
    } else {
      var points = [];

      for (var i = 0; i <= sides; i++) {
        var angle = start_radial +
                    i * ((end_radial - start_radial) % 360) / sides;
        var point = sphere.offset(origin,
                                  outer_radius,
                                  (angle + heading) / 180 * Math.PI);
        points.push(ol.proj.fromLonLat(point));
      }

      for (var i = sides; i >= 0; i--) {
        var angle = start_radial +
                    i * ((end_radial - start_radial) % 360) / sides;
        var point = sphere.offset(origin,
                                  inner_radius,
                                  (angle + heading) / 180 * Math.PI);
        points.push(ol.proj.fromLonLat(point));
      }

      if (update)
        geometry.setCoordinates([points]);
      else
        geometry = new ol.geom.Polygon([points]);
    }
  };

  _.extend(sector, Backbone.Events);
  sector.init();
  return sector;
};
