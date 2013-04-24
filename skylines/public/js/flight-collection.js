/**
 * An ordered collection of flight objects.
 * @constructor
 */
slFlightCollection = function() {
  var collection = {};

  // Private attributes

  /**
   * The internal data store
   * @type {Array}
   * @private
   */
  var data_ = [];

  // Public attributes and methods

  collection.length = 0;

  /**
   * Returns the flight at the specified index in the collection.
   * @param  {Number} index
   * @return {?Object}
   */
  collection.at = function(index) {
    return data_[index];
  };

  /**
   * Iterates through the flights in the collection and calls the callback
   * function for every flight.
   * @param  {Function} callback
   */
  collection.each = function(callback) {
    for (var i = 0, len = data_.length; i < len; ++i)
      callback(collection.at(i));
  };


  /**
   * Returns the flight with the specified id, or null.
   * @param  {Number} id
   * @return {?Object}
   */
  collection.get = function(id) {
    for (var i = 0, len = data_.length; i < len; ++i) {
      var flight = collection.at(i);
      if (flight.sfid == id)
        return flight;
    }

    return null;
  };


  /**
   * Returns true if a flight with the specified id is part of the collection.
   * @param  {Number} id
   * @return {Boolean}
   */
  collection.has = function(id) {
    return collection.get(id) != null;
  };


  /**
   * Adds another flight to the collection.
   * @param {Object} flight
   */
  collection.add = function(flight) {
    data_.push(flight);
    collection.length = data_.length;
  };


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
