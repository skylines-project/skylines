// add leading zeros to a number
function pad(num, size) {
  var s = "000000000" + num;
  return s.substr(s.length-size);
}

/**
 * Function: pinFlight
 *
 * Saves the flight id into a cookie
 *
 * Parameters:
 * sfid - {int} SkyLines flight ID
 */
function pinFlight(sfid) {
  var pinnedFlights = getPinnedFlights();
  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] == sfid) return;
  }

  pinnedFlights.push(sfid);
  $.cookie('SkyLines_pinnedFlights', pinnedFlights.join(","), { path: "/" });
}

/**
 * Function: unpinFlight
 *
 * Removes a pinned flight
 *
 * Parameters:
 * sfid - {int} SkyLines flight ID
 */
function unpinFlight(sfid) {
  var pinnedFlights = getPinnedFlights();
  var temp = [];

  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] != sfid) temp.push(pinnedFlights[i]);
  }

  $.cookie('SkyLines_pinnedFlights', temp.join(","), { path: "/" });
}


/**
 * Function: getPinnedFlights
 *
 * Gets all pinned flights from the cookie
 *
 * Returns:
 * {Array(int)} Array of SkyLine flight IDs
 */
function getPinnedFlights() {
  var cookie = $.cookie('SkyLines_pinnedFlights');

  if (cookie) {
    var pinnedFlights = cookie.split(",");

    for (var i = 0; i < pinnedFlights.length; i++) {
      pinnedFlights[i] = parseInt(pinnedFlights[i]);
    }

    return pinnedFlights;
  }

  return [];
}

/**
 * Function: isPinnedFlight
 *
 * Parameters:
 * sfid - {int} SkyLines flight ID
 *
 * Returns:
 * {bool} pinned flight or not pinned flight
 */
function isPinnedFlight(sfid) {
  var pinnedFlights = getPinnedFlights();

  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] == sfid) return true;
  }

  return false;
}

/**
 * Function: pinButton
 *
 * Parameters:
 * element - {Object} jQuery element which will be the button
 * sfid - {int} SkyLines flight ID
 */
function pinButton(element, sfid) {
  var onClick = function() {
    if (!isPinnedFlight(sfid)) {
      pinFlight(sfid);
      element.html("<i class='icon-star'></i> Flight pinned!");
    } else {
      unpinFlight(sfid);
      element.html("<i class='icon-star-empty'></i> Click to pin");
    }
  };

  // initial setting
  if (!isPinnedFlight(sfid)) {
    element.html("<i class='icon-star-empty'></i> Click to pin");
  } else {
    element.html("<i class='icon-star'></i> Flight pinned!");
  }

  // add event handler
  element.click(onClick);
}

