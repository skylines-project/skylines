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
    data_.forEach(callback);
  };


  /**
   * Returns the object with the specified id, or null.
   * @param  {Number} id
   * @return {?Object}
   */
  collection.get = function(id) {
    return data_.find(function(object) {
      return object.getID() == id;
    }) || null;
  };

  /**
   * Returns all objects with the specified id, or null.
   * @param  {Number} id
   * @return {?Object}
   */
  collection.all = function(id) {
    var objects = data_.filter(function(object) {
      return object.getID() == id;
    });

    return objects || null;
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
    data_.pushObject(object);

    $(collection).triggerHandler('add', [object]);
  };


  /**
   * Removes the object with the specified id.
   * @param  {Number} id
   * @return {Boolean} true if success
   */
  collection.remove = function(id) {
    var object = collection.get(id);
    if (object === null) {
      return false;
    }

    $(collection).triggerHandler('preremove', object);
    data_.removeObject(object);
    $(collection).triggerHandler('removed', id);

    return true;
  };


  return collection;
};
