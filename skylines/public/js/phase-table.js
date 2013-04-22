

function slPhaseTable(placeholder) {
  /**
   * The selected table row or null.
   * @type {?(String|number)}
   * @private
   */
  this.selection_ = null;

  this.changePointers_(placeholder);
  this.setupEvents_(placeholder);
}


/**
 * Clears the current selection from the table.
 *
 * @param  {boolean=} opt_trigger
 *   The 'selection_changed' event is triggered if this parameter is true.
 */
slPhaseTable.prototype.clearSelection = function(opt_trigger) {
  this.setSelection(null, opt_trigger);
};


/**
 * Selects a new flight phase from the table.
 *
 * @param {?Object} element The table row that should be selected.
 * @param  {boolean=} opt_trigger
 *   The 'selection_changed' event is triggered if this parameter is true.
 */
slPhaseTable.prototype.setSelection = function(element, opt_trigger) {
  if (this.selection_)
    $(this.selection_).removeClass('selected');

  this.selection_ = element;

  if (this.selection_)
    $(this.selection_).addClass('selected');

  if (opt_trigger) {
    if (this.selection_) {
      var start = parseFloat(
          $(this.selection_).children('td.start').attr('data-content'));
      var duration = parseFloat(
          $(this.selection_).children('td.duration').attr('data-content'));

      $(this).trigger('selection_changed', [{
        start: start,
        end: start + duration,
        duration: duration
      }]);
    } else {
      $(this).trigger('selection_changed');
    }
  }
};


/**
 * Change the cursor styles of all rows in the placeholder to pointers.
 * @param  {DOMElement} placeholder
 * @private
 */
slPhaseTable.prototype.changePointers_ = function(placeholder) {
  placeholder.find('tr').each(function(index, row) {
    $(row).css('cursor', 'pointer');
  });
};


/**
 * Setup the click event handlers for the rows in the placeholder.
 * @param  {DOMElement} placeholder
 * @private
 */
slPhaseTable.prototype.setupEvents_ = function(placeholder) {
  var that = this;
  placeholder.on('click', 'tr', function(event) {
    that.setSelection(selection == this ? null : this, true);
  });
};
