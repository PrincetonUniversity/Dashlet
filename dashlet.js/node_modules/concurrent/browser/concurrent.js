/**
 * Concurrent
 * @author Phips Peter <pspeter333@gmail.com>
 *
 * UMD Module loader from https://github.com/umdjs/umd/blob/master/returnExports.js
 */
(function(root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module.
    define(factory);
  } else if (typeof exports === 'object') {
    // Node. Does not work with strict CommonJS, but
    // only CommonJS-like enviroments that support module.exports,
    // like Node.
    module.exports = factory();
  } else {
    // Browser globals (root is window)
    root.concurrent = factory();
  }
}(this, function() {
/**
 * Executes a function asynchronously. Prefers setImmediate but will fallback to
 * setTimeout for older browers.
 *
 * @type {Function}
 * @private
 */
var next = typeof setImmediate === 'function' ? setImmediate : function(fn) {
  setTimeout(fn, 0);
};

/**
 * Proxy for node's util class taken from the node source code.
 * https://github.com/joyent/node/blob/master/lib/util.js
 * 
 * @type {Object}
 */
var util = {
  isArray: function(ar) {
    return Array.isArray(ar);
  },
  inherits: function(ctor, superCtor) {
    ctor.super_ = superCtor;
    ctor.prototype = Object.create(superCtor.prototype, {
      constructor: {
        value: ctor,
        enumerable: false,
        writable: true,
        configurable: true
      }
    });
  }
};

/**
 * Promises states according to the A+ Specification
 *
 * @readOnly
 * @enum {Number}
 */
var State = {
  PENDING: "pending",
  FULFILLED: "fulfilled",
  REJECTED: "rejected"
};




/**
 * Resolves the promises asynchronously
 *
 * @param {Promise} promise The promise to resolve
 */
var resolve = function(promise) {
  var resolver;

  resolver = function() {
    var callback = promise.callbacks.shift();

    if (callback && callback[promise.state]) {
      callback[promise.state](promise.value);
    }

    if (promise.callbacks.length > 0) {
      next(resolver);
    }
  };

  next(resolver);
};

/**
 * Transitions a promise from one state to another
 *
 * @param  {Promise} promise The promise to transition
 * @param  {State}   state   The new state of the promise
 * @param  {Object}  value   The value or reason of the promise
 * @return {State}           The state of the promise
 */
var transition = function(promise, state, value) {
  if (promise.state === State.FULFILLED || promise.state === State.REJECTED) {
    return promise.state;
  }

  promise.state = state;
  promise.value = value;

  resolve(promise);

  return promise.state;
};

/**
 * Handles the promise chain and returns a new promise
 *
 * @param  {Promise}   promise The promise to initialize
 * @param  {State}     state   The state for the promise to transition to
 * @param  {Function}  fn      The callback from then
 * @return {Function}          The callback to be registered
 */
var handle = function(promise, state, fn) {
  return function(value) {
    if (typeof fn !== 'function') {
      return transition(promise, state, value);
    }

    try {
      var result = fn(value);

      if (result && typeof result.then === 'function') {
        result.then(function(value) {
          promise.fulfill(value);
        }, function(reason) {
          promise.reject(reason);
        });

        return promise.state;
      }

      return promise.fulfill(result);
    } catch (reason) {
      return promise.reject(reason);
    }
  };
};

/**
 * Promise implementing the Promises/A+ Specification
 * @class
 */
var Promise = function() {
  this.state = State.PENDING;
  this.callbacks = [];
};

/**
 * A+ Then specification
 *
 * @param  {Function} onFulfilled Called when the promise succeeds
 * @param  {Function} onRejected  Called when the promise fails
 * @return {Promise}              The new promise
 */
Promise.prototype.then = function(onFulfilled, onRejected) {
  var promise = new this.constructor();
  var callbacks = {};

  callbacks[State.FULFILLED] = handle(promise, State.FULFILLED, onFulfilled);
  callbacks[State.REJECTED] = handle(promise, State.REJECTED, onRejected);
  this.callbacks.push(callbacks);

  if (this.state !== State.PENDING) {
    resolve(this);
  }

  return promise;
};

/**
 * Fulfills the promise with a value
 *
 * @param  {Object} value
 * @return {State} The state of the promise
 */
Promise.prototype.fulfill = function(value) {
  transition(this, State.FULFILLED, value);
};

/**
 * Rejects the promise with a reason
 *
 * @param  {Error} reason The reason the promise failed
 * @return {State} The state of the promise
 */
Promise.prototype.reject = function(reason) {
  transition(this, State.REJECTED, reason);
};



var ValidationError = function(value) {
  Error.captureStackTrace(this, this);
  this.value = value;
  this.message = '' + this.value + ' did not match predicate';
};

util.inherits(ValidationError, Error);

ValidationError.prototype.name = 'ValidationError';



var TimeoutError = function(time) {
  Error.captureStackTrace(this, this);
  this.time = time;
  this.message = 'Future did not resolve in ' + this.time + ' ms';
};

util.inherits(TimeoutError, Error);

TimeoutError.prototype.name = 'TimeoutError';






/**
 * Future
 * Future class matchin Promises/A+ Spec and Scala API
 * @class
 */
var Future = function() {
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



var collections = {};

/**
 * Iterates over the collection an fulfills with the array
 * 
 * @param  {Array}    arr      The array to iterate over
 * @param  {Function} iterator The function to be called each time
 * @return {Future}            The future for the work
 */
var forEach = collections.forEach = function(arr, iterator) {
  var future = new Future();
  var completed = 0;

  arr.forEach(function(element, index, arr) {
    next(function() {
      try {
        iterator(element, index, arr);
      } catch (reason) {
        future.reject(reason);
      }

      if (++completed >= arr.length) {
        future.fulfill(completed);
      }
    });
  });

  return future;
};

/**
 * Proxy for every method
 *
 * @param  {Array}    arr       Array to check
 * @param  {Function} predicate Function to check with
 * @return {Future}             Future fulfilled with true if all matched
 */
var every = collections.every = function(arr, predicate) {
  var future = new Future();

  var compute = forEach(arr, function(element, index, arr) {
    if (!predicate(element, index, arr)) {
      future.fulfill(false);
    }
  });

  compute.then(function(value) {
    future.fulfill(true);
  }, function(reason) {
    future.reject(reason);
  });

  return future;
};

/**
 * Proxy for some method
 *
 * @param  {Array}    arr       Array to check
 * @param  {Function} predicate Function to check with
 * @return {Future}             Future fulfilled with true if any matched
 */
var some = collections.some = function(arr, predicate) {
  var future = new Future();

  var compute = forEach(arr, function(element, index, arr) {
    if (predicate(element, index, arr)) {
      future.fulfill(true);
    }
  });

  compute.then(function(value) {
    future.fulfill(false);
  }, function(reason) {
    future.reject(reason);
  });

  return future;
};

/**
 * Proxy for filter method
 *
 * @param  {Array}    arr       Array to check
 * @param  {Function} predicate Function to check with
 * @return {Future}             Future fulfilled with all that matched
 */
var filter = collections.filter = function(arr, predicate) {
  var future = new Future();
  var elements = [];

  var compute = forEach(arr, function(element, index, arr) {
    if (predicate(element, index, arr)) {
      elements.push(element);
    }
  });

  compute.then(function(value) {
    future.fulfill(elements);
  }, function(reason) {
    future.reject(reason);
  });

  return future;
};

/**
 * Proxy for map method
 *
 * @param  {Array}    arr       Array to check
 * @param  {Function} transform Function to map with
 * @return {Future}             Future fulfilled with mapped elements
 */
var map = collections.map = function(arr, transform) {
  var future = new Future();
  var elements = [];

  var compute = forEach(arr, function(element, index, arr) {
    elements.push(transform(element, index, arr));
  });

  compute.then(function(value) {
    future.fulfill(elements);
  }, function(reason) {
    future.reject(reason);
  });

  return future;
};

/**
 * Proxy for reverse method
 *
 * @param  {Array} arr  The array to reverse
 * @return {Future}     The future with the reverse list
 */
var reverse = collections.reverse = function(arr) {
  var future = new Future();
  var elements = [];

  var compute = forEach(arr, function(element) {
    elements.unshift(element);
  });

  compute.then(function(value) {
    future.fulfill(elements);
  }, function(reason) {
    future.reject(reason);
  });

  return future;
};

/**
 * Proxy for reduce method
 *
 * @param  {Array}    arr       Array to check
 * @param  {Function} transform Function to reduce with
 * @param  {Object}   initial   Optional initial value
 * @return {Future}             Future fulfilled with reduced value
 */
var reduce = collections.reduce = function(arr, transform, initial) {
  var future = new Future();
  var accumulator, list;

  if (initial) {
    accumulator = initial;
    list = arr;
  } else {
    accumulator = arr[0];
    list = arr.slice(1);
  }

  var compute = forEach(arr, function(element, index, arr) {
    accumulator = transform(accumulator, element, index, arr);
  });

  compute.then(function(value) {
    future.fulfill(accumulator);
  }, function(reason) {
    future.reject(reason);
  });

  return future;
};

/**
 * Proxy for reduceRight method.
 * The method inverses the array and then reduces it
 *
 * @param  {Array}    arr       Array to check
 * @param  {Function} transform Function to reduce with
 * @param  {Object}   initial   Optional initial value
 * @return {Future}             Future fulfilled with reduced value
 */
var reduceRight = collections.reduceRight = function(arr, transform, initial) {
  return reverse(arr).then(function(elements) {
    return reduce(elements, transform, initial);
  });
};

return {
  State: State,
  Promise: Promise,
  Future: Future,
  errors: {
    ValidationError: ValidationError,
    TimeoutError: TimeoutError
  },
  collections: collections
};
}));