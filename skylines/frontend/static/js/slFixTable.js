/**
 * Module to handle the fix table
 * @constructor
 * @param {jQuery} placeholder jQuery object of the placeholder
 */
var slFixTable = Backbone.View.extend({
  /**
   * Initialize the FixTable view with the currently
   * known flights in our FlightCollection.
   *
   * Each FixTableRowView will update itself when a
   * flight has been changed.
   */
  initialize: function() {
    this.render();

    // Listen to changes in the FlightCollection
    this.listenTo(this.collection, 'add', this.render);
    this.listenTo(this.collection, 'remove', this.render);

    return this;
  },

  /**
   * Renders the fix data table into the placeholder.
   * This function has to be called after the internal data store has been
   * modified by any of the following methods.
   */
  render: function() {
    this.$el.html('');

    // Loop through data and render each one
    this.collection.each(function(flight) {
      var flight_view = new slFixTableRowView({
        model: flight,
        collection: this.collection,
        attributes: {
          selectable: this.collection.length > 1
        }
      });

      flight_view.listenTo(this, 'update:time', flight_view.render);

      this.$el.append(flight_view.el);
    }.bind(this));

    return this;
  }
});

var slFixTableRowView = Backbone.View.extend({
  tagName: 'tr',

  /**
   * Adds a new and empty row to the fix table.
   *
   * @param {string|number} id
   * @param {string} color The color of the flight trace on the map.
   * @param {string=} opt_competition_id Optional competition id of the plane.
   * @param {bool=} opt_remove_icon Optional remove icon for this flight.
   * @return {DOMElement} The generated fix table row.
   */
  initialize: function() {
    // function addHTMLRow(id, color, opt_competition_id, opt_remove_icon) {
    var sfid = this.model.attributes.sfid;
    var color = this.model.getColor();
    var opt_competition_id = this.model.getCompetitionID();
    var opt_remove_icon = !(this.collection.at(0) == this.model);

    // Generate a new table row for the flight
    var row = $(
        '<td><span class="badge" style="background:' + color + '">' +
        (opt_competition_id || '&nbsp;') +
        '</span></td>' +
        '<td>--:--:--</td>' +
        '<td>--</td>' +
        '<td>--</td>' +
        '<td>--</td>' +
        '<td>--</td>' +
        '<td>' +
            (opt_remove_icon ?
                '<i id="remove-flight-' + sfid + '" data-sfid="' +
                sfid + '" class="icon-remove"></i>' :
                ''
            ) +
        '</td>');

    // render row to element.
    this.$el.html(row);

    // set selectable
    this.setSelectable();

    // Attach onClick event handler
    this.$el.on('click', function(e) {
      if (!this.attributes.selectable)
        return;

      this.collection.select(this.model);
      return false; // prevent event bubbling
    }.bind(this));

    this.$el.find('#remove-flight-' + sfid).on('click', function(e) {
      this.collection.remove(this.model);
      unpinFlight(sfid);
      return false; // prevent event bubbling
    }.bind(this));

    // toggle selection if flight is selected
    this.toggleSelection();

    // listen to selection updates to rerender the row
    this.listenTo(this.collection, 'change:selection', this.toggleSelection);

    return this;
  },

  /**
   * Updates a given row with the data from the given fix.
   *
   * @param {DOMElement} row
   * @param {Object} fix
   */
  render: function(time) {
    var fix = this.model.getFixData(time);

    // Loop through the columns and fill them
    this.$el.find('td').each(function(index, cell) {
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

    return this;
  },

  /**
   * Sets whether single flights should be selectable by clicking on the list.
   *
   * @param {Boolean} value True enables the "selectable" mode.
   */
  setSelectable: function() {
    this.$el.css('cursor', this.attributes.selectable ? 'pointer' : '');
  },

  /**
   * Selects a new flight from the table in "selectable" mode.
   *
   * @param {?(String|number)} id Identifier of the flight or null.
   * @param  {Boolean=} opt_trigger
   *   The 'selection_changed' event is triggered if this parameter is true.
   */
  toggleSelection: function() {
    if (this.model.getSelection() && this.collection.length > 1)
      this.$el.addClass('selected');
    else
      this.$el.removeClass('selected');
  }
});
