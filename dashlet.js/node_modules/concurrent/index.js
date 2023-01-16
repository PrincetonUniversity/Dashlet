exports.Promise = require('./lib/promise');
exports.Future = require('./lib/future');
exports.State = require('./lib/state');
exports.errors = {
  ValidationError: require('./lib/errors/validation'),
  TimeoutError: require('./lib/errors/timeout')
};
exports.collections = require('./lib/collections');
