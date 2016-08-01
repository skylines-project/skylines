import Ember from 'ember';

export default Ember.Service.extend({
  init() {
    let user = Ember.$('meta[name=skylines-user]').attr('content');
    if (user) {
      user = user.split('||', 2);
      this.set('user', {
        id: parseInt(user[0], 10),
        name: user[1],
      });
    }

    let club = Ember.$('meta[name=skylines-club]').attr('content');
    if (club) {
      club = club.split('||', 2);
      this.set('club', {
        id: parseInt(club[0], 10),
        name: club[1],
      });
    }
  },
});
