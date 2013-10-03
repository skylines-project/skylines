// add leading zeros to a number
function pad(num, size) {
  var s = '000000000' + num;
  return s.substr(s.length - size);
}


/**
 * Saves the flight id into a cookie
 *
 * @param {int} sfid SkyLines flight ID.
 */
function pinFlight(sfid) {
  var pinnedFlights = getPinnedFlights();
  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] == sfid) return;
  }

  pinnedFlights.push(sfid);
  $.cookie('SkyLines_pinnedFlights', pinnedFlights.join(','), { path: '/' });

  // show pinned flights link in list view if found in DOM
  showPinnedFlightsLink();
}


/**
 * Removes a pinned flight
 *
 * @param {int} sfid SkyLines flight ID.
 */
function unpinFlight(sfid) {
  var pinnedFlights = getPinnedFlights();
  var temp = [];

  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] != sfid) temp.push(pinnedFlights[i]);
  }

  $.cookie('SkyLines_pinnedFlights', temp.join(','), { path: '/' });

  // toggle the pinned flights link in list view if found in DOM
  showPinnedFlightsLink();
}


/**
 * Gets all pinned flights from the cookie
 *
 * @return {Array(int)} Array of SkyLines flight IDs.
 */
function getPinnedFlights() {
  var cookie = $.cookie('SkyLines_pinnedFlights');

  if (cookie) {
    var pinnedFlights = cookie.split(',');

    for (var i = 0; i < pinnedFlights.length; i++) {
      pinnedFlights[i] = parseInt(pinnedFlights[i]);
    }

    return pinnedFlights;
  }

  return [];
}


/**
 * @param {int} sfid SkyLines flight ID.
 * @return {bool} pinned flight or not pinned flight.
 */
function isPinnedFlight(sfid) {
  var pinnedFlights = getPinnedFlights();

  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] == sfid) return true;
  }

  return false;
}


/**
 * @param {Object} element jQuery element which will be the button.
 * @param {int} sfid SkyLines flight ID.
 */
function pinButton(element, sfid) {
  var onClick = function() {
    if (!isPinnedFlight(sfid)) {
      pinFlight(sfid);
      element.html("<i class='icon-star icon-large'></i> Flight pinned!");
    } else {
      unpinFlight(sfid);
      element.html("<i class='icon-star-empty icon-large'></i> Click to pin");
    }
  };

  // initial setting
  element.addClass('btn btn-default');
  if (!isPinnedFlight(sfid)) {
    element.html("<i class='icon-star-empty icon-large'></i> Click to pin");
  } else {
    element.html("<i class='icon-star icon-large'></i> Flight pinned!");
  }

  // add event handler
  element.click(onClick);
}


/**
 * Returns the URL for the current page and add pinned flights
 * to the URL which are only stored client-side inside a cookie.
 *
 * @param {String} url original URL.
 * @return {String} URL for the current flights including pinned flights.
 */
function getShareUrl(url) {
  var pinnedFlights = getPinnedFlights();

  var url_re = /(.*?)\/([\d,]{1,})\/(.*)/;
  var url_split = url_re.exec(url);

  var ids = url_split[2].split(',').concat(pinnedFlights);

  var unique_ids = [];
  for (var i in ids) {
    if ($.inArray(parseInt(ids[i]), unique_ids) == -1) {
      unique_ids.push(parseInt(ids[i]));
    }
  }

  return url_split[1] + '/' + unique_ids.join(',') + '/' + url_split[3];
}


/**
 * Shows the pinned flights link at element id #pinned-flights-link
 */
function showPinnedFlightsLink() {
  var pinned_flights = getPinnedFlights();
  if (pinned_flights.length > 0) {
    $('#pinned-flights-link').show();
  } else {
    $('#pinned-flights-link').hide();
  }
}
