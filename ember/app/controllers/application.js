import Controller from '@ember/controller';

export default Controller.extend({
  actions: {
    search(text) {
      this.transitionToRoute('search', {
        queryParams: { text },
      });
      return false;
    },
  },
});
