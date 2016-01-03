var slGraphicTaskEditor = function(_map, waypoint_file_collection, task) {
  var task_editor = {};

  var map = _map;

  var modify_mode = false;
  var marker_point = null;
  var down_event = null;

  task_editor.init = function() {
    var pointer_interaction = new ol.interaction.Pointer({
      handleEvent: handleEvent
    });

    map.addInteraction(pointer_interaction);

    var marker_style = new ol.style.Circle({
      radius: 8,
      fill: new ol.style.Fill({
        color: [0x22, 0x00, 0xdb, 0.3]
      }),
      stroke: new ol.style.Stroke({
        width: '2',
        color: '#2200db'
      })
    });

    map.on('postcompose', function(e) {
      var vector_context = e.vectorContext;

      if (marker_point != null) {
        vector_context.setImageStyle(marker_style);
        vector_context.drawPointGeometry(marker_point.point);
      }
    });

    $(map.getTargetElement()).on('mouseout', function(e) {
      setMarkerPoint();
    });
  };

  task_editor.getModifyMode = function() {
    return modify_mode;
  };

  function handleDBLClickEvent(event) {
    if (task.getLength() != 0 && !modify_mode) {
      // Finish task drawing and go into modify mode.

      // Remove last turnpoint as our doubleclick fired another click event
      task.removeLastTurnpoint();

      modify_mode = true;
      task_editor.trigger('change:modify_mode', true);
    } else if (modify_mode) {
      if (marker_point && marker_point.turnpoint) {
        if (task.removeTurnpoint(marker_point.turnpoint)) {
          setMarkerPoint();
        }
      }
    }

    return false;
  };

  function handleClickEvent(event) {
    if (task.getLength() == 0 && !modify_mode) {
      var snap_waypoint = snapToWaypoint(event);

      if (snap_waypoint) {
        // first turnpoint
        var tp1 = task.addTurnpoint(snap_waypoint.getCoordinate());

        // last turnpoint
        var tp2 = task.addTurnpoint(snap_waypoint.getCoordinate());

        tp1.setWaypoint(snap_waypoint);
        tp2.setWaypoint(snap_waypoint);
      } else {
        // first turnpoint
        task.addTurnpoint(event.coordinate);

        // last turnpoint
        task.addTurnpoint(event.coordinate);
      }

      return false;
    } else if (task.getLength() != 0 && !modify_mode) {
      // We are in task creation mode.

      // check if previous turnpoint is too near
      // (dblclick fires two click events)
      var last_tp = task.getPreviousTurnpoint();
      var close_pixel = map.getPixelFromCoordinate(last_tp.getCoordinate());

      var dx = event.pixel[0] - close_pixel[0];
      var dy = event.pixel[1] - close_pixel[1];
      var distance = dx * dx + dy * dy;

      // Add new turnpoint if distance is large enough.
      if (distance > 100) {
        var snap_waypoint = snapToWaypoint(event);

        if (snap_waypoint) {
          var turnpoint = task.addTurnpoint(snap_waypoint.getCoordinate());
          turnpoint.setWaypoint(snap_waypoint);
        } else {
          task.addTurnpoint(event.coordinate);
        }
      }

      return false;
    }

    return true;
  };

  function handleMoveEvent(event) {
    // return early if task length is 0
    if ((task.getLength() == 0) || event.dragging)
      return true;

    var coordinate = event.coordinate;
    var snap = false;

    if (!modify_mode) {
      // snap to any other turnpoint but the last
      var snap_waypoint = snapToWaypoint(event);
      var snap_turnpoint = snapToTurnpoint(event, task.getLastTurnpoint());
    } else {
      // snap to any turnpoint
      var snap_waypoint = null;
      var snap_turnpoint = snapToTurnpoint(event);
    }

    if (snap_waypoint != null) {
      coordinate = snap_waypoint.getCoordinate();
      snap = true;
    } else if (snap_turnpoint != null) {
      coordinate = snap_turnpoint.getCoordinate();
      snap = true;
    } else if (modify_mode) {
      var close = snapToTask(event);

      if (close != null) {
        coordinate = close.slice(0, 2);
        snap = true;
      }
    }

    if (!modify_mode) {
      // We are in task creation mode. Modify last turnpoint
      if (snap_waypoint)
        task.getLastTurnpoint().setWaypoint(snap_waypoint);
      else
        task.getLastTurnpoint().setCoordinate(coordinate);

      setMarkerPoint(coordinate, snap_turnpoint);
    } else {
      // We are in modify mode. Let's see...
      if (snap) {
        setMarkerPoint(coordinate, snap_turnpoint);
      } else {
        setMarkerPoint();
      }
    }

    return true;
  };

  function handleDragEvent(event) {
    // return early if not in modify_mode or no marker_point is set
    if (!(modify_mode && marker_point))
      return true;

    var coordinate = event.coordinate;
    var snap_waypoint = snapToWaypoint(event);
    var snap_turnpoint = snapToTurnpoint(event, marker_point.turnpoint);
    var position = null;

    if (snap_waypoint != null) {
      coordinate = snap_waypoint.getCoordinate();
    } else if (snap_turnpoint != null) {
      coordinate = snap_turnpoint.getCoordinate();
    } else {
      var close = snapToTask(event);

      if (close != null) {
        position = close[2];
      }
    }

    if (marker_point.turnpoint) {
      var turnpoint = marker_point.turnpoint;

      if (snap_waypoint)
        turnpoint.setWaypoint(snap_waypoint);
      else
        turnpoint.setCoordinate(coordinate);

      setMarkerPoint(turnpoint.getCoordinate(), turnpoint);

      return false;
    } else if (position) {
      var turnpoint = task.addTurnpoint(coordinate, Math.ceil(position));
      setMarkerPoint(turnpoint.getCoordinate(), turnpoint);
      return false;
    }

    return true;
  };

  function handleDownEvent(event) {
    down_event = {
      coordinate: event.coordinate,
      pixel: event.pixel
    };

    var coordinate = event.coordinate;
    var snap = false;

    var snap_turnpoint = snapToTurnpoint(event);

    if (snap_turnpoint != null) {
      coordinate = snap_turnpoint.getCoordinate();
      snap = true;
    } else {
      var close = snapToTask(event);

      if (close != null) {
        coordinate = close.slice(0, 2);
        snap = true;
      }
    }

    if (snap) {
      setMarkerPoint(coordinate, snap_turnpoint);

      // start adding a turnpoint. don't move map.
      if (modify_mode)
        return false;
    } else {
      setMarkerPoint();
    }

    return true;
  };

  function handleUpEvent(event) {
    if (down_event) {
      var dx = event.pixel[0] - down_event.pixel[0];
      var dy = event.pixel[1] - down_event.pixel[1];
      var distance = dx * dx + dy * dy;

      down_event = null;

      if (distance < 2)
        return handleClickEvent(event);
    }

    return true;
  };

  function handleEvent(event) {
    if (event.type == 'dblclick') {
      return handleDBLClickEvent(event);
    } else if (event.type == 'pointerdown') {
      return handleDownEvent(event);
    } else if (event.type == 'pointerup') {
      return handleUpEvent(event);
    } else if (event.type == 'pointermove') {
      return handleMoveEvent(event);
    } else if (event.type == 'pointerdrag') {
      return handleDragEvent(event);
    }
    return true;
  };

  function snapToWaypoint(event) {
    distance_map = [];
    waypoint_map = [];

    var extent = ol.extent.buffer(ol.extent.boundingExtent([event.coordinate]),
                                  map.getView().getResolution() * 20);

    waypoint_file_collection.each(function(waypoints) {
      var source = waypoints.getSource();
      var waypoints = source.getFeaturesInExtent(extent);

      if (waypoints == null) {
        distance_map.push(9e9);
        return;
      }

      var current_distance_map = [];

      for (i = 0, ii = waypoints.length; i < ii; ++i) {
        var close_pixel = map.getPixelFromCoordinate(
            waypoints[i].getGeometry().getFirstCoordinate()
            );

        var dx = event.pixel[0] - close_pixel[0];
        var dy = event.pixel[1] - close_pixel[1];
        var distance = dx * dx + dy * dy;

        current_distance_map.push(distance);
      }

      var min_index = _.indexOf(current_distance_map,
                                _.min(current_distance_map));

      distance_map.push(current_distance_map[min_index]);
      waypoint_map.push(waypoints[min_index]);
    });

    var minimum = _.min(distance_map);

    if (minimum < 100) {
      var index = _.indexOf(distance_map, minimum);

      // return a copy of that waypoint
      return waypoint_file_collection.at(index)
             .getWaypoint(waypoint_map[index].getId());
    } else {
      return null;
    }
  };

  function snapToTurnpoint(event, ignore) {
    distance_map = [];

    task.getTurnpoints().each(function(tp) {
      if (tp === ignore) {
        distance_map.push(9e9);
        return;
      }

      var close_pixel = map.getPixelFromCoordinate(tp.getCoordinate());

      var dx = event.pixel[0] - close_pixel[0];
      var dy = event.pixel[1] - close_pixel[1];
      var distance = dx * dx + dy * dy;

      distance_map.push(distance);
    });

    var minimum = _.min(distance_map);

    if (minimum < 100) {
      return task.getTurnpoints().at(_.indexOf(distance_map, minimum));
    } else {
      return null;
    }
  };

  function snapToTask(event) {
    if (task.getLength() == 0) {
      // nothing to snap to
      return null;
    }

    var close = task.getGeometry().getClosestPoint(event.coordinate);
    var close_pixel = map.getPixelFromCoordinate(close);

    var dx = event.pixel[0] - close_pixel[0];
    var dy = event.pixel[1] - close_pixel[1];
    var distance = dx * dx + dy * dy;

    if (distance < 100) {
      return close;
    } else {
      return null;
    }
  };

  function setMarkerPoint(coordinate, turnpoint) {
    if (!coordinate && marker_point != null) {
      marker_point = null;
      map.render();
      task_editor.trigger('remove:marker', null);
      return;
    } else if (!coordinate) {
      return;
    }

    if (marker_point != null) {
      // update only
      marker_point.point.setCoordinates(coordinate);
      marker_point.coordinate = coordinate;
      marker_point.turnpoint = turnpoint || null;
      task_editor.trigger('change:marker', marker_point);
    } else {
      // create marker point
      marker_point = {
        point: new ol.geom.Point(coordinate),
        coordinate: coordinate,
        turnpoint: turnpoint || null
      };
      task_editor.trigger('create:marker', marker_point);
    }
    map.render();
  };

  _.extend(task_editor, Backbone.Events);
  task_editor.init();
  return task_editor;
};
