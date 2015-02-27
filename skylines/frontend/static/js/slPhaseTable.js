slPhaseTable = function(placeholder) {
  var phase_table = {};

  // Private attributes

  /**
   * The selected table row or null.
   * @type {?(String|number)}
   */
  var selection = null;

  // Public attributes and methods

  /**
   * Selects a new flight phase from the table.
   *
   * @param {?Object} element The table row that should be selected.
   * @param  {Boolean=} opt_trigger
   *   The 'selection_changed' event is triggered if this parameter is true.
   */
  phase_table.setSelection = function(element, opt_trigger) {
    if (selection)
      $(selection).removeClass('selected');

    selection = element;

    if (selection)
      $(selection).addClass('selected');

    if (opt_trigger) {
      if (selection) {
        var start = parseFloat(
            $(selection).children('td.start').attr('data-content'));
        var duration = parseFloat(
            $(selection).children('td.duration').attr('data-content'));

        $(phase_table).trigger('selection_changed', [{
          start: start,
          end: start + duration,
          duration: duration
        }]);
      } else {
        $(phase_table).trigger('selection_changed');
      }
    }
  };

  // Initialization

  changePointer();
  setupEvents();

  return phase_table;

  // Private methods

  /**
   * Change the cursor styles of all rows in the placeholder to pointers.
   */
  function changePointer() {
    placeholder.find('tr').each(function(index, row) {
      $(row).css('cursor', 'pointer');
    });
  }

  /**
   * Setup the click event handlers for the rows in the placeholder.
   */
  function setupEvents() {
    placeholder.on('click', 'tr', function(event) {
      phase_table.setSelection(selection == this ? null : this, true);
    });
  }
};
