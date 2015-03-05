/**
 * Searches the next smaller index to a number in a monotonic array.
 * If value == array[idx] it returns the next smaller index idx - 1
 * (the only way to return array.length - 1 is to search for values larger
 * than the last element). For values smaller than the first element
 * it returns 0.
 *
 * @param {Array} array Array.
 * @param {double} value Number.
 * @return {int} Index next smaller to Number in Array.
 */
function getNextSmallerIndex(array, value) {
  var low = 1;
  var high = array.length - 1;

  while (low < high) {
    var mid = (low + high) >> 1;
    if (value < array[mid]) high = mid;
    else low = mid + 1;
  }
  return low - 1;
}


/**
 * @param {int} seconds Seconds of day.
 * @return {String} formatted time "HH:MM:SS".
 */
function formatSecondsAsTime(seconds) {
  seconds %= 86400;
  var h = Math.floor(seconds / 3600);
  var m = Math.floor((seconds % 3600) / 60);
  var s = Math.floor(seconds % 3600 % 60);

  // Format the result into time strings
  return pad(h, 2) + ':' + pad(m, 2) + ':' + pad(s, 2);
}


function geographicDistance(loc1_deg, loc2_deg) {
  var radius = 6367009;

  var loc1 = [loc1_deg[0] * Math.PI / 180, loc1_deg[1] * Math.PI / 180];
  var loc2 = [loc2_deg[0] * Math.PI / 180, loc2_deg[1] * Math.PI / 180];

  var dlon = loc2[0] - loc1[0];
  var dlat = loc2[1] - loc1[1];

  var a = Math.pow(Math.sin(dlat / 2), 2) +
          Math.cos(loc1[1]) * Math.cos(loc2[1]) *
          Math.pow(Math.sin(dlon / 2), 2);
  var c = 2 * Math.asin(Math.sqrt(a));

  return radius * c;
}
