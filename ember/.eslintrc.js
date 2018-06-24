module.exports = {
  root: true,
  parserOptions: {
    ecmaVersion: 2017,
  },
  plugins: ['prettier'],
  extends: [
    'simplabs',
    'simplabs/plugins/ember',
    'prettier',
  ],
  rules: {
    'ember/local-modules': 'off',
    'ember/order-in-components': 'off',
    'ember/order-in-controllers': 'off',
    'ember/order-in-models': 'off',
    'ember/order-in-routes': 'off',
    'prettier/prettier': 'error',
  },
};
