import Component from '@ember/component';
import { readOnly } from '@ember/object/computed';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  tagName: '',
  count: 0,
  page: 1,
  perPage: 100,
  firstPage: 1,

  pages: safeComputed('count', 'perPage', (count, perPage) => Math.ceil(count / perPage)),
  lastPage: readOnly('pages'),

  prevPage: safeComputed('page', 'firstPage', (page, firstPage) => Math.max(firstPage, page - 1)),
  prevDisabled: safeComputed('page', 'firstPage', (page, firstPage) => page <= firstPage),

  nextPage: safeComputed('page', 'lastPage', (page, lastPage) => Math.min(lastPage, page + 1)),
  nextDisabled: safeComputed('page', 'lastPage', (page, lastPage) => page >= lastPage),

  showMinusFour: safeComputed(
    'page',
    'firstPage',
    'lastPage',
    (page, firstPage, lastPage) => page - 4 >= firstPage && page === lastPage,
  ),

  showMinusThree: safeComputed(
    'page',
    'firstPage',
    'lastPage',
    (page, firstPage, lastPage) => page - 3 >= firstPage && page >= lastPage - 1,
  ),

  showMinusTwo: safeComputed('page', 'firstPage', (page, firstPage) => page - 2 >= firstPage),

  showMinusOne: safeComputed('page', 'firstPage', (page, firstPage) => page - 1 >= firstPage),

  showPlusOne: safeComputed('page', 'lastPage', (page, lastPage) => page + 1 <= lastPage),

  showPlusTwo: safeComputed('page', 'lastPage', (page, lastPage) => page + 2 <= lastPage),

  showPlusThree: safeComputed(
    'page',
    'lastPage',
    'firstPage',
    (page, lastPage, firstPage) => page + 3 <= lastPage && page <= firstPage + 1,
  ),

  showPlusFour: safeComputed(
    'page',
    'lastPage',
    'firstPage',
    (page, lastPage, firstPage) => page + 4 <= lastPage && page === firstPage,
  ),
});
