/* eslint no-bitwise: 0 */

/**
 * Searches the next smaller index to a number in a monotonic array.
 * If value == array[idx] it returns the next smaller index idx - 1
 * (the only way to return array.length - 1 is to search for values larger
 * than the last element). For values smaller than the first element
 * it returns 0.
 *
 * @param {Array} array Array.
 * @param {Number} value Number.
 * @return {int} Index next smaller to Number in Array.
 */
export default function(array, value) {
  let low = 1;
  let high = array.length - 1;

  while (low < high) {
    let mid = (low + high) >> 1;
    if (value < array[mid]) {
      high = mid;
    } else {
      low = mid + 1;
    }
  }
  return low - 1;
}
