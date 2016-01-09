var AirportsFormat = function(opt_options) {
  var options = opt_options || {};
};

ol.inherits(AirportsFormat, ol.format.JSONFeature);

AirportsFormat.prototype.readFeaturesFromObject = function(
    object, opt_options) {
  if (object instanceof Array) {
    var features = [];
    var i, ii;
    for (i = 0, ii = object.length; i < ii; ++i) {
      features.push(this.readFeatureFromObject(object[i],
          opt_options));
    }
    return features;
  } else if (object instanceof Object) {
    return [this.readFeatureFromObject(object, opt_options)];
  } else {
    return [];
  }
};

AirportsFormat.prototype.readFeatureFromObject = function(
    object, opt_options) {
  var geometry = this.readGeometry_(object.location,
      opt_options);
  var feature = new ol.Feature();

  feature.setGeometry(geometry);

  if (object.id)
    feature.setId(object.id);

  if (object.elevation)
    feature.set('elevation', object.elevation);

  if (object.name)
    feature.set('name', object.name);

  return feature;
};

AirportsFormat.prototype.readGeometry_ = function(object, opt_options) {
  if (!object) {
    return null;
  }

  var coordinates = ol.proj.fromLonLat([object.longitude, object.latitude]);
  return new ol.geom.Point(coordinates);
};

// Dummy method. We always expect EPSG:4326
AirportsFormat.prototype.readProjectionFromObject = function(object) {
  return 'EPSG:4236';
};
