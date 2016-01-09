var slTaskVectorSource = function(task_collection) {
  var task_vector_source = {};

  var source = new ol.source.Vector();

  task_vector_source.init = function() {
    task_collection.on('add', addToSource);
    task_collection.on('remove', removeFromSource);
  };

  function addToSource(task) {
    console.log('add task');
    var feature = new ol.Feature({
      geometry: task.getGeometry(),
      task_id: task.cid,
      type: 'task'
    });

    source.addFeature(feature);
  };

  function removeFromSource(task) {
    source.removeFeature(
        source.getFeatures().filter(function(e) {
          return e.get('task_id') == task.cid &&
                 e.get('type') == 'task';
        })[0]
    );
  };

  /**
   * Returns the vector layer source of this collection.
   * @return {ol.source.Vector}
   */
  task_vector_source.getSource = function() {
    return source;
  };

  task_vector_source.init();
  return task_vector_source;
};
