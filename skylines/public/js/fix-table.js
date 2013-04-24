slFixTable = function(placeholder) {
  var fix_table = {};

  // Private attributes

  /**
   * The internal data store for the metadata and fix data.
   * @type {Object}
   */
  var data = {};

  /**
   * Defines if the flights in the list are selectable by clicking on them.
   * @type {Boolean}
   */
  var selectable = false;

  /**
   * The identifier of the selected flight or null.
   * @type {?(String|number)}
   */
  var selection = null;

  // Public attributes and functions

  /**
   * @expose
   * Renders the fix data table into the placeholder.
   * This function has to be called after the internal data store has been
   * modified by any of the following methods.
   */
  fix_table.render = function() {
    // Loop through data and render/update each one
    for (var id in data) {
      var row = data[id];
      renderRow(row.element, row.fix);
    }
  };

  /**
   * @expose
   * Adds a new row to the fix data table.
   *
   * @param {String|number} id An identifier for the flight row.
   * @param {String} color RGB hex color (e.g. '#FF0000').
   * @param {String} competition_id
   *   An optional competition id of the aircraft.
   */
  fix_table.addRow = function(id, color, opt_competition_id) {
    // Don't add the row if is exists already
    if (id in data)
      return false;

    // Generate new HTML table row element
    var element = addHTMLRow(id, color, opt_competition_id);

    // Save the relevant metadata for later
    data[id] = {
      element: element,
      fix: {}
    };

    return true;
  };

  /**
   * @expose
   * Clears all fix data from the internal data store.
   */
  fix_table.clearAllFixes = function() {
    for (var id in data)
      data[id].fix = null;
  };

  /**
   * @expose
   * Clears the fix data of one specific row.
   *
   * @param {String|number} id
   *   The identifier of the row that should be cleared.
   * @return {Boolean} True if the row was cleared, False otherwise.
   */
  fix_table.clearFix = function(id) {
    return fix_table.updateFix(id);
  };

  /**
   * @expose
   * Updates the fix data of one specific row.
   *
   * @param {String|number} id
   *   The identifier of the row that should be updated.
   * @param  {Object} fix The new fix data for the row.
   * @return {Boolean} True if the row was updated, False otherwise.
   */
  fix_table.updateFix = function(id, fix) {
    if (!(id in data))
      return false;

    data[id].fix = fix;
    return true;
  };

  /**
   * @expose
   * Returns whether the fix data table is in "selectable" mode.
   *
   * @return {Boolean} True if "selectable" mode is active, False otherwise.
   */
  fix_table.getSelectable = function() {
    return selectable;
  };

  /**
   * @expose
   * Sets whether single flights should be selectable by clicking on the list.
   *
   * @param {Boolean} value True enables the "selectable" mode.
   */
  fix_table.setSelectable = function(value) {
    selectable = value;

    placeholder.find('tr').each(function(index, row) {
      $(row).css('cursor', selectable ? 'pointer' : '');
    });
  };

  /**
   * @expose
   * Clears the current selection from the table.
   *
   * @param  {Boolean=} opt_trigger
   *   The 'selection_changed' event is triggered if this parameter is true.
   */
  fix_table.clearSelection = function(opt_trigger) {
    fix_table.setSelection(null, opt_trigger);
  };

  /**
   * @expose
   * Returns the identifier of the selected flight or null.
   *
   * @return {?(String|number)} Identifier of the selected flight or null.
   */
  fix_table.getSelection = function() {
    return selection;
  };

  /**
   * @expose
   * Selects a new flight from the table in "selectable" mode.
   *
   * @param {?(String|number)} id Identifier of the flight or null.
   * @param  {Boolean=} opt_trigger
   *   The 'selection_changed' event is triggered if this parameter is true.
   */
  fix_table.setSelection = function(id, opt_trigger) {
    if (selection)
      data[selection].element.removeClass('selected');

    selection = id;

    if (selection)
      data[selection].element.addClass('selected');

    if (opt_trigger)
      $(fix_table).trigger('selection_changed', [selection]);
  };

  return fix_table;

  // Private functions

  function renderRow(row, fix) {
    // Loop through the columns and fill them
    $(row).find('td').each(function(index, cell) {
      var html = '--';

      if (index == 1) {
        if (fix && fix.time !== undefined)
          html = formatSecondsAsTime(fix.time);
        else
          html = '--:--:--';

      } else if (index == 2) {
        if (fix && fix['alt-msl'] !== undefined)
          html = slUnits.formatAltitude(fix['alt-msl']) +
              ' <small>MSL</small>';

      } else if (index == 3) {
        if (fix && fix['alt-gnd'] !== undefined)
          html = slUnits.formatAltitude(fix['alt-gnd']) +
              ' <small>GND</small>';

      } else if (index == 4) {
        if (fix && fix.vario !== undefined) {
          html = slUnits.formatLift(fix.vario);
          if (fix.lift >= 0)
            html = '+' + html;
        }

      } else if (index == 5) {
        if (fix && fix.speed !== undefined)
          html = slUnits.formatSpeed(fix.speed);

      } else {
        // Don't update/overwrite the other columns
        return;
      }

      $(cell).html(html);
    });
  }

  function addHTMLRow(id, color, opt_competition_id) {
    // Generate a new table row for the flight
    var row = $(
        '<tr>' +
        '<td><span class="badge" style="background:' + color + '">' +
        (opt_competition_id || '') +
        '</span></td>' +
        '<td>--:--:--</td>' +
        '<td>--</td>' +
        '<td>--</td>' +
        '<td>--</td>' +
        '<td>--</td>' +
        '</tr>');

    // Attach onClick event handler
    row.on('click', function(e) {
      if (!selectable)
        return;

      fix_table.setSelection(selection == id ? null : id, true);
    });

    // Attach the new row to the table
    placeholder.append(row);

    return row;
  }
};
