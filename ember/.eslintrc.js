module.exports = {
  root: true,
  parserOptions: {
    ecmaVersion: 2017,
  },
  extends: [
    'simplabs',
    'simplabs/plugins/ember',
  ],
  rules: {
    'comma-dangle': ['error', 'always-multiline'],
    'generator-star-spacing': ['error', 'both'],
    'ember/local-modules': 'off',
    'ember/order-in-components': 'off',
    'ember/order-in-controllers': 'off',
    'ember/order-in-models': 'off',
    'ember/order-in-routes': 'off',
  },
};
