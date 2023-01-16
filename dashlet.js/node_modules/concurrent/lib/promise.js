var next = require('./next');
var State = require('./state');

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
var Promise = module.exports = function() {
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
