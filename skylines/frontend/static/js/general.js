/**
 * Pads a number with leading zeros
 *
 * @param {Number} num Number to pad
 * @param {Number} size Width of returned string
 * @return {String} Padded number
 */
function pad(num, size) {
  var s = '000000000' + num;
  return s.substr(s.length - size);
}


/**
 * Returns the URL for the current page and add pinned flights
 * to the URL which are only stored client-side inside a cookie.
 *
 * @param {String} url The original URL.
 * @return {String} URL for the current flights including pinned flights.
 */
function getShareUrl(url) {
  var pinnedFlights = window.pinnedFlightsService.get('pinned');

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
