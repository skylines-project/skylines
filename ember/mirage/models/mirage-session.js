import { Model, belongsTo } from 'ember-cli-mirage';

/**
 * This is a mirage-only model, that is used to keep track of the current
 * session and the associated `user` model, because in route handlers we don't
 * have access to the auth data that the actual auth service is using for
 * these things.
 *
 * This mock implementation means that there can only ever exist one
 * session at a time.
 */
export default Model.extend({
  user: belongsTo(),
});
