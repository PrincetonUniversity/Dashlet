var Future = require('./future');
var next = require('./next');

var collections = module.exports = {};

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
