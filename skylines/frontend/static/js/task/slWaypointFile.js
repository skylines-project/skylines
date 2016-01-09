var slWaypointFile = Backbone.Model.extend({
  idAttribute: 'file_id',

  defaults: function() {
    return {
      waypoints: null,
      source: null,
      url: null,
      file_id: null,
      type: null,
      loader: null,
      loadedExtentsRtree: new ol.structs.RBush()
    };
  },

  initialize: function() {
    this.attributes.source = new ol.source.Vector();

    this.attributes.loader = ol.featureloader.loadFeaturesXhr(
        function(extent, resolution, projection) {
          var e1 = ol.proj.toLonLat([extent[0], extent[1]]);
          var e2 = ol.proj.toLonLat([extent[2], extent[3]]);
          return this.attributes.url + '?bbox=' + [e1, e2].join(',');
        }.bind(this),
        new AirportsFormat(),
        this.updateSuccess,
        this.updateFail
        );
  },

  update: function(extent) {
    var loadedExtentsRtree = this.attributes.loadedExtentsRtree;

    var alreadyLoaded = loadedExtentsRtree.forEachInExtent(extent,
        /**
         * @param {{extent: ol.Extent}} object Object.
         * @return {boolean} Contains.
         */
        function(object) {
          return ol.extent.containsExtent(object.extent, extent);
        });

    if (!alreadyLoaded) {
      this.attributes.loader.call({that: this, extent: extent}, extent);
    }
  },

  updateSuccess: function(features) {
    this.that.attributes.source.addFeatures(features);

    if (this.extent) {
      this.that.attributes.loadedExtentsRtree.insert(
          this.extent,
          { extent: this.extent.slice() }
      );
      this.extent = null;
    }
  },

  updateFail: function() {
    if (this.extent) {
      this.extent = null;
    }
  },

  getSource: function() {
    return this.attributes.source;
  },

  getWaypoint: function(id) {
    var full_wp_id = this.attributes.file_id + '_' + id;

    var waypoint = this.attributes.waypoints.findWhere({id: full_wp_id});

    if (waypoint)
      return waypoint;

    var feature = this.attributes.source.getFeatureById(id);

    // No waypoint copy available. Create one...
    waypoint = new slWaypoint({
      coordinate: feature.getGeometry().getFirstCoordinate(),
      name: feature.get('name'),
      type: feature.get('type'),
      waypoint_id: full_wp_id
    });

    this.attributes.waypoints.add(waypoint);
    return waypoint;
  },

  getID: function() {
    return this.attributes.file_id;
  }
});
