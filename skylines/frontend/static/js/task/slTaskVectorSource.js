var slTaskVectorSource = function(task_collection) {
  var task_vector_source = {};

  var source = new ol.source.Vector();

  task_vector_source.init = function() {
    task_collection.on('add', addToSource);
    task_collection.on('remove', removeFromSource);
    task_collection.on('add:turnpoint', addTurnpoint);
    task_collection.on('remove:turnpoint', removeTurnpoint);
    task_collection.on('change:turnpoint:type', changeTurnpoint);
  };

  function addToSource(task) {
    console.log('add task');
    var feature = new ol.Feature({
      geometry: task.getGeometry(),
      task_id: task.cid,
      task: task,
      type: 'task'
    });

    source.addFeature(feature);
  };

  function removeFromSource(task) {
    console.log('remove task');
    source.removeFeature(
        source.getFeatures().filter(function(e) {
          return e.get('task_id') == task.cid &&
                 e.get('type') == 'task';
        })[0]
    );
  };

  function addTurnpoint(task, turnpoint) {
    console.log('add turnpoint');
    var feature = new ol.Feature({
      geometry: turnpoint.getGeometry(),
      task_id: task.cid,
      turnpoint_id: turnpoint.cid,
      task: task,
      turnpoint: turnpoint,
      type: 'turnpoint'
    });

    source.addFeature(feature);
  };

  function removeTurnpoint(task, turnpoint) {
    console.log('remove turnpoint');
    source.removeFeature(
        source.getFeatures().filter(function(e) {
          return e.get('task_id') == task.cid &&
                 e.get('turnpoint_id') == turnpoint.cid &&
                 e.get('type') == 'turnpoint';
        })[0]
    );
  };

  function changeTurnpoint(task, turnpoint) {
    console.log('change turnpoint');
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
