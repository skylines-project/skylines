module.exports = {
  root: true,
  extends: [
    'simplabs',
    'simplabs/plugins/ember',
  ],
  rules: {
    'comma-dangle': ['error', 'always-multiline'],
    'generator-star-spacing': ['error', 'both'],
    'ember/local-modules': 'off',
    'ember/order-in-components': ['error', {
      order: [
        'service',
        'property',
        ['single-line-function', 'multi-line-function'],
        'observer',
        'lifecycle-hook',
        'actions',
        'method',
      ],
    }],
    'ember/order-in-controllers': ['error', {
      order: [
        'service',
        'query-params',
        'inherited-property',
        'property',
        ['single-line-function', 'multi-line-function'],
        'observer',
        'actions',
        'method',
      ],
    }]
  },
};
