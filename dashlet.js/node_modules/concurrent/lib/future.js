var Promise = require('./promise');
var State = require('./state');
var TimeoutError = require('./errors/timeout');
var util = require('util');
var ValidationError = require('./errors/validation');

/**
 * Future
 * Future class matchin Promises/A+ Spec and Scala API
 * @class
 */
var Future = module.exports = function() {
  Promise.call(this);
};

util.inherits(Future, Promise);

/**
 * Checks if the future is completed
 *
 * @return {Boolean} Whether or not the future is completed
 */
Future.prototype.isCompleted = function() {
  return this.state !== State.PENDING;
};

/**
 * Assigns one callback for both fulfill and reject
 *
 * @param {Function} callback The callback for both results
 */
Future.prototype.onComplete = function(callback) {
  this.then(function(value) {
    callback(value);
  }, function(reason) {
    callback(reason);
  });
};

/**
 * Converts a traditional style callback and resolves the future. If the future
 * has more than one argument beyond err, it will return and array as the value.
 *
 * @optional
 * @param {Array} keys The keys for the callback
 *
 * @return {Function}  The callback for async
 */
Future.prototype.convert = function(keys) {
  var self = this;
  return function() {
    var args = Array.prototype.slice.call(arguments);
    var err = args.shift();

    if (err) {
      return self.reject(err);
    }

    if (args.length === 1) {
      args = args.shift();
    }

    if (util.isArray(keys)) {
      args = keys.reduce(function(results, key, index) {
        results[key] = args[index];
        return results;
      }, {});
    }

    return self.fulfill(args);
  };
};

/**
 * Returns a future that rejects after some time
 *
 * @param  {Number} duration Number of milliseconds to reject at
 * @return {Future}          The instremented future
 */
Future.prototype.ready = function(duration) {
  var future = new this.constructor();

  this.then(function(value) {
    future.fulfill(value);
  });

  setTimeout(function() {
    try {
      throw new TimeoutError(duration);
    } catch (err) {
      future.reject(err);
    }
  }, duration);

  return future;
};

/**
 * Falls back to the result of the other future if this one fails
 *
 * @param  {Promise} promise The promise to fallback to
 * @return {Future}          The future with the fallback value
 */
Future.prototype.fallbackTo = function(promise) {
  return this.then(null, function(reason) {
    return promise;
  });
};

/**
 * Filters the future by ensuring it matches the predicate
 *
 * @param  {Function} predicate The predicate to test the value of the future
 * @return {Future}             The new future
 */
Future.prototype.filter = function(predicate) {
  return this.then(function(value) {
    if (!predicate(value)) {
      throw new ValidationError(value);
    }

    return value;
  });
};

/**
 * Creates a new future based on the map callback
 *
 * @param  {Function} callback The callback on the successful value
 * @return {Future}            The new future
 */
Future.prototype.map = function(callback) {
  return this.then(callback);
};

/**
 * Calls the callback on failure
 *
 * @param {Function} callback The callback to be called if the promise fails
 */
Future.prototype.onFailure = function(callback) {
  this.then(null, callback);
};

/**
 * Calls the callback on success
 *
 * @param {Function} callback The callback to be called if the promise succeeds
 */
Future.prototype.onSuccess = function(callback) {
  this.then(callback);
};

/**
 * Recovers the future if it fails
 *
 * @param  {Object} value The value to recover to
 * @return {Future}       The new future
 */
Future.prototype.recover = function(value) {
  var future = new this.constructor();

  this.then(function(value) {
    future.fulfill(value);
  }, function(reason) {
    future.fulfill(value);
  });

  return future;
};

/**
 * Recovers a future with a function that returns a promise.
 *
 * @param  {Function} callback A function returning a promise
 * @return {Future}            The new future
 */
Future.prototype.recoverWith = function(callback) {
  return this.then(null, callback);
};

/**
 * Alias for then
 *
 * @param  {Function} onFulfilled Called when the future succeeds
 * @param  {Function} onRejected  Called when the future fails
 * @return {Future}               The new future
 */
Future.prototype.transform = Future.prototype.then;

/**
 * Takes two futures and zips their values as a tuple
 *
 * @param  {Promise} promise The promise to be applied on the right of the tuple
 * @return {Future}          The new future which will fulfill with the tuple
 */
Future.prototype.zip = function(promise) {
  return this.then(function(left) {
    return promise.then(function(right) {
      return [left, right];
    });
  });
};

/**
 * Creates a future fulfilled with a value
 *
 * @param  {Object} value The value of the future to be fulfilled with
 * @return {Future}       The fulfilled future
 */
Future.fulfilled = function(value) {
  var future = new Future();
  future.fulfill(value);
  return future;
};

/**
 * Creates a future rejected with a reason
 *
 * @param  {Object} reason The reason the future was rejected
 * @return {Future}        The rejected future
 */
Future.rejected = function(reason) {
  var future = new Future();
  future.reject(reason);
  return future;
};

/**
 * Sequences a list of futures together
 *
 * @param  {Object} tasks Either an object or an array of tasks
 * @return {Future}       The future of all the results
 */
Future.sequence = function(tasks) {
  var future = new Future();
  var results, length;
  var completed = 0;

  var handle = function(task, key) {
    task.then(function(value) {
      results[key] = value;
      if (++completed >= length) {
        future.fulfill(results);
      }
    }, function(reason) {
      future.reject(reason);
    });
  };

  if (util.isArray(tasks)) {
    results = [];
    length = tasks.length;
    tasks.forEach(handle);
  } else {
    results = {};
    length = Object.keys(tasks).length;
    for (var key in tasks) {
      handle(tasks[key], key);
    }
  }

  return future;
};

/**
 * Wraps a Promise with a Future
 *
 * @param  {Promise} promise The promise to wrap
 * @return {Future}          The new future
 */
Future.wrap = function(promise) {
  var future = new Future();
  promise.then(function(value) {
    future.fulfill(value);
  }, function(reason) {
    future.reject(reason);
  });
  return future;
};