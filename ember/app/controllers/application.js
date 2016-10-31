import Ember from 'ember';

export default Ember.Controller.extend({
  actions: {
    search(text) {
      this.transitionToRoute('search', {
        queryParams: { text },
      });
      return false;
    },

    resetUploadController() {
      this.get('uploadController').set('result', null);
    },
  },
});
