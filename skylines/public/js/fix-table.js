


/**
 * A table that shows times, altitudes, speeds, ... of GPS traces
 * at a specific time.
 *
 * @param  {DOMElement} placeholder
 * @constructor
 */
function slFixTable(placeholder) {
  /**
   * The HTML element that will hold the fix table.
   * @type {DOMElement}
   * @private
   */
  this.placeholder_ = placeholder;

  /**
   * The internal data store for the metadata and fix data.
   * @type {Object}
   * @private
   */
  this.data_ = {};

  /**
   * Defines if the flights in the list are selectable by clicking on them.
   * @type {boolean}
   * @private
   */
  this.selectable_ = false;

  /**
   * The identifier of the selected flight or null.
   * @type {?(string|number)}
   * @private
   */
  this.selection_ = null;
}


/**
 * Renders the fix data table into the placeholder.
 *
 * This function has to be called after the internal data store has been
 * modified by any of the following methods.
 */
slFixTable.prototype.render = function() {
  // Loop through data and render/update each one
  for (var id in this.data_) {
    var row = this.data_[id];
    slFixTable.renderRow_(row.element, row.fix);
  }
};


/**
 * Adds a new row to the fix data table.
 *
 * @param {string|number} id An identifier for the flight row.
 * @param {string} color RGB hex color (e.g. '#FF0000').
 * @param {string=} opt_competition_id
 *     An optional competition id of the aircraft.
 * @return {boolean} false if the id is already present in the table,
 *     true otherwise.
 */
slFixTable.prototype.addRow = function(id, color, opt_competition_id) {
  // Don't add the row if is exists already
  if (id in this.data_)
    return false;

  // Generate new HTML table row element
  var element = this.addHTMLRow_(id, color, opt_competition_id);

  // Save the relevant metadata for later
  this.data_[id] = {
    element: element,
    fix: {}
  };

  return true;
};


/**
 * Clears all fix data from the internal data store.
 */
slFixTable.prototype.clearAllFixes = function() {
  for (var id in this.data_)
    this.data_[id].fix = null;
};


/**
 * Clears the fix data of one specific row.
 *
 * @param {string|number} id
 *   The identifier of the row that should be cleared.
 * @return {boolean} True if the row was cleared, False otherwise.
 */
slFixTable.prototype.clearFix = function(id) {
  return this.updateFix(id);
};


/**
 * Updates the fix data of one specific row.
 *
 * @param {string|number} id
 *   The identifier of the row that should be updated.
 * @param  {?Object} fix The new fix data for the row.
 * @return {boolean} True if the row was updated, False otherwise.
 */
slFixTable.prototype.updateFix = function(id, fix) {
  if (!(id in this.data_))
    return false;

  this.data_[id].fix = fix;
  return true;
};


/**
 * Returns whether the fix data table is in "selectable" mode.
 *
 * @return {boolean} True if "selectable" mode is active, False otherwise.
 */
slFixTable.prototype.getSelectable = function() {
  return this.selectable_;
};


/**
 * Sets whether single flights should be selectable by clicking on the list.
 *
 * @param {boolean} value True enables the "selectable" mode.
 */
slFixTable.prototype.setSelectable = function(value) {
  this.selectable_ = value;

  this.placeholder_.find('tr').each(function(index, row) {
    $(row).css('cursor', this.selectable_ ? 'pointer' : '');
  });
};


/**
 * Clears the current selection from the table.
 *
 * @param  {boolean=} opt_trigger
 *   The 'selection_changed' event is triggered if this parameter is true.
 */
slFixTable.prototype.clearSelection = function(opt_trigger) {
  this.setSelection(null, opt_trigger);
};


/**
 * Returns the identifier of the selected flight or null.
 *
 * @return {?(string|number)} Identifier of the selected flight or null.
 */
slFixTable.prototype.getSelection = function() {
  return this.selection_;
};


/**
 * Selects a new flight from the table in "selectable" mode.
 *
 * @param {?(String|number)} id Identifier of the flight or null.
 * @param  {Boolean=} opt_trigger
 *   The 'selection_changed' event is triggered if this parameter is true.
 */
slFixTable.prototype.setSelection = function(id, opt_trigger) {
  if (this.selection_)
    this.data_[this.selection_].element.removeClass('selected');

  this.selection_ = id;

  if (this.selection_)
    this.data_[this.selection_].element.addClass('selected');

  if (opt_trigger)
    $(this).trigger('selection_changed', [this.selection_]);
};


/**
 * Updates a given row with the data from the given fix.
 * @param  {DOMElement} row
 * @param  {Object} fix
 * @private
 */
slFixTable.renderRow_ = function(row, fix) {
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
};


/**
 * Adds a new and empty row to the fix table.
 *
 * @param {string|number} id
 * @param {string} color The color of the flight trace on the map.
 * @param {string=} opt_competition_id Optional competition id of the plane.
 * @return {DOMElement} The generated fix table row.
 * @private
 */
slFixTable.prototype.addHTMLRow_ = function(id, color, opt_competition_id) {
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
  var that = this;
  row.on('click', function(e) {
    if (!that.selectable_)
      return;

    that.setSelection(that.selection_ == id ? null : id, true);
  });

  // Attach the new row to the table
  this.placeholder_.append(row);

  return row;
};
