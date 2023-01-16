var util = require('util');

var ValidationError = module.exports = function(value) {
  Error.captureStackTrace(this, this);
  this.value = value;
  this.message = '' + this.value + ' did not match predicate';
};

util.inherits(ValidationError, Error);

ValidationError.prototype.name = 'ValidationError';
