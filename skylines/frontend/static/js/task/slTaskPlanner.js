var slTaskPlanner = function(map, task_panel_placeholder) {
  var task_planner = {};

  var task_edit_interaction = null;

  var task_collection = new slTaskCollection();
  var task_panel = new slTaskPanel({
    el: task_panel_placeholder
  });
  var task_vector_source = new slTaskVectorSource(task_collection);

  /**
   * Determin the drawing style for the feature
   * @param {ol.feature} feature Feature to style
   * @return {!Array<ol.style.Style>} Style of the feature
   */
  function style_function(feature) {
    var color = '#2200db'; // default color
    if ('color' in feature.getKeys())
      color = feature.get('color');

    return [new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: color,
        width: 2
      })
    })];
  }

  task_planner.init = function() {
    var task_layer = new ol.layer.Vector({
      source: task_vector_source.getSource(),
      style: style_function,
      name: 'Task',
      zIndex: 60,
      updateWhileInteracting: true
    });

    map.getMap().addLayer(task_layer);

    // add a first task to the collection
    var task = new slTask();
    task_collection.add(task);
    task_panel.setTask(task);

    task_edit_interaction = new slGraphicTaskEditor(map.getMap(), task);
  };

  task_planner.init();
  return task_planner;
};
