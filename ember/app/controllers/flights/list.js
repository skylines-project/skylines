import Controller from '@ember/controller';

export default class ListController extends Controller {
  queryParams = ['page', 'column', 'order'];
  page = 1;
  column = 'date';
  order = 'desc';
}
