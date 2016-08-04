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

  var url_ids = url_split[2].split(',').map(function(it) { return parseInt(it, 10); });
  var unique_ids = url_ids.concat(pinnedFlights).uniq();

  return url_split[1] + '/' + unique_ids.join(',') + '/' + url_split[3];
}
