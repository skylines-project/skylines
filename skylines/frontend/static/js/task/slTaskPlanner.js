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
    var fill = [0, 0, 0, 1]; // default fill (transparent)

    switch (feature.get('type')) {
      case 'task':
        color = '#2200db';
        break;

      case 'turnpoint':
        color = '#f9e400';
        fill = [0xf9, 0xe4, 0x00, 0.25];
        break;
    }

    return [new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: color,
        width: 2
      }),
      fill: new ol.style.Fill({
        color: fill
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

    // create turnpoint selector, but disable for now
    var turnpoint_selector = new slTurnpointSelect(map.getMap(), task_layer, task);
    turnpoint_selector.disable();

    task_edit_interaction.on('create:marker', function() {
      turnpoint_selector.disable();
    });

    task_edit_interaction.on('remove:marker change:modify_mode', function() {
      if (task_edit_interaction.getModifyMode())
        turnpoint_selector.enable();
    });
  };

  task_planner.init();
  return task_planner;
};
