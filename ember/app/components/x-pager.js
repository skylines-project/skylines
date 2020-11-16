import { readOnly } from '@ember/object/computed';
import Component from '@glimmer/component';

import safeComputed from '../computed/safe-computed';

export default class extends Component {
  firstPage = 1;

  @safeComputed('args.count', 'args.perPage', (count, perPage) => Math.ceil(count / perPage)) pages;
  @readOnly('pages') lastPage;

  @safeComputed('args.page', 'firstPage', (page, firstPage) => Math.max(firstPage, page - 1)) prevPage;
  @safeComputed('args.page', 'firstPage', (page, firstPage) => page <= firstPage) prevDisabled;

  @safeComputed('args.page', 'lastPage', (page, lastPage) => Math.min(lastPage, page + 1)) nextPage;
  @safeComputed('args.page', 'lastPage', (page, lastPage) => page >= lastPage) nextDisabled;

  @safeComputed(
    'args.page',
    'firstPage',
    'lastPage',
    (page, firstPage, lastPage) => page - 4 >= firstPage && page === lastPage,
  )
  showMinusFour;

  @safeComputed(
    'args.page',
    'firstPage',
    'lastPage',
    (page, firstPage, lastPage) => page - 3 >= firstPage && page >= lastPage - 1,
  )
  showMinusThree;

  @safeComputed('args.page', 'firstPage', (page, firstPage) => page - 2 >= firstPage) showMinusTwo;
  @safeComputed('args.page', 'firstPage', (page, firstPage) => page - 1 >= firstPage) showMinusOne;
  @safeComputed('args.page', 'lastPage', (page, lastPage) => page + 1 <= lastPage) showPlusOne;
  @safeComputed('args.page', 'lastPage', (page, lastPage) => page + 2 <= lastPage) showPlusTwo;

  @safeComputed(
    'args.page',
    'lastPage',
    'firstPage',
    (page, lastPage, firstPage) => page + 3 <= lastPage && page <= firstPage + 1,
  )
  showPlusThree;

  @safeComputed(
    'args.page',
    'lastPage',
    'firstPage',
    (page, lastPage, firstPage) => page + 4 <= lastPage && page === firstPage,
  )
  showPlusFour;
}
