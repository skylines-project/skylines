/**
 * An ordered collection of arbitrary objects.
 * @constructor
 */
slCollection = function() {
  var collection = {};

  // Private attributes

  /**
   * The internal data store
   * @type {Array}
   * @private
   */
  var data_ = [];

  // Public attributes and methods

  /**
   * Returns the number of objects in the collection.
   * @return {Number}
   */
  collection.length = function() {
    return data_.length;
  };

  /**
   * Returns the object at the specified index in the collection.
   * @param  {Number} index
   * @return {?Object}
   */
  collection.at = function(index) {
    return data_[index];
  };

  /**
   * Iterates through the objects in the collection and calls the callback
   * function for every object.
   * @param  {Function} callback
   */
  collection.each = function(callback) {
    for (var i = 0, len = collection.length(); i < len; ++i)
      callback(collection.at(i));
  };


  /**
   * Returns the object with the specified id, or null.
   * @param  {Number} id
   * @return {?Object}
   */
  collection.get = function(id) {
    for (var i = 0, len = collection.length(); i < len; ++i) {
      var object = collection.at(i);
      if (object.sfid == id)
        return object;
    }

    return null;
  };


  /**
   * Returns true if a object with the specified id is part of the collection.
   * @param  {Number} id
   * @return {Boolean}
   */
  collection.has = function(id) {
    return collection.get(id) != null;
  };


  /**
   * Adds another object to the collection.
   * @param {Object} object
   */
  collection.add = function(object) {
    data_.push(object);

    $(collection).triggerHandler('add', [object]);
  };


  return collection;
};



/**
 * An ordered collection of flight objects.
 * @constructor
 */
slFlightCollection = function() {
  var collection = slCollection();

  // Public attributes and methods

  /**
   * Calculates the bounds of all flights in the collection.
   * @return {OpenLayers.Bounds}
   */
  collection.getBounds = function() {
    var bounds = new OpenLayers.Bounds();

    collection.each(function(flight) {
      bounds.extend(flight.geo.bounds);
    });

    return bounds;
  };

  return collection;
};
