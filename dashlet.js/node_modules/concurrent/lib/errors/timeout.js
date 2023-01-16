var util = require('util');

var TimeoutError = module.exports = function(time) {
  Error.captureStackTrace(this, this);
  this.time = time;
  this.message = 'Future did not resolve in ' + this.time + ' ms';
};

util.inherits(TimeoutError, Error);

TimeoutError.prototype.name = 'TimeoutError';