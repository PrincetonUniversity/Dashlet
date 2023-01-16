Concurrent
==========

Promises/A+ with Scala Awesomeness [![Build Status](https://travis-ci.org/pspeter3/concurrent.png)](https://travis-ci.org/pspeter3/concurrent)

Examples
--------

```js
var Future = require('concurrent').Future;
var request = require('request');

var req = function(options) {
  var future = new Future();
  request(options, future.convert(['res', 'body']));
  return future;
};

/**
 * Example #1: Simple Async Call
 */
// Fetch Google with a SLA
var google = req('http://google.com').ready(1000);

// Fetch the status
var status = google.map(function(value) {
  return value.res.statusCode;
});

// Log the final result
status.onSuccess(function(statusCode) {
  console.log(statusCode);
});

/**
 * Examples #2: Parallel Calls
 */
var duckDuckGo = req('http://duckduckgo.com');
var bingOrYahoo = req('http://bing.com').fallbackTo(req('http://yahoo.com'));

var asArray = Future.sequence([google, duckDuckGo, bingOrYahoo]);

asArray.onSuccess(function(values) {
  console.log(values);
});

var asObject = Future.sequence({
  google: google,
  duckDuckGo: duckDuckGo,
  bingOrYahoo: bingOrYahoo
});

var recoverable = asObject.recover({
  promises: 'A+'
});
```

Benchmarks
----------

Here are the top 5 libraries for some of the tests

```text
==========================================================
Test: promise-fulfill x 10000
----------------------------------------------------------
laissez:    |   3.00
concurrent: ▇▇  14.00
deferred:   ▇▇  19.00
when:       ▇▇▇▇▇  36.00
q:          ▇▇▇▇▇▇▇▇  57.00

==========================================================
Test: promise-reject x 10000
----------------------------------------------------------
concurrent: |   6.00
avow:       ▇▇▇▇▇▇▇▇  55.00
q:          ▇▇▇▇▇▇▇▇▇  60.00
when:       ▇▇▇▇▇▇▇▇▇▇▇▇▇  89.00
laissez:    ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 118.00

==========================================================
Test: promise-sequence x 10000
----------------------------------------------------------
laissez:    |   8.00
when:       ▇▇▇▇▇▇▇▇ 204.00
concurrent: ▇▇▇▇▇▇▇▇ 207.00
avow:       ▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 335.00
deferred:   ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 421.00

==========================================================
Test: defer-fulfill x 10000
----------------------------------------------------------
laissez:    ▇  21.00
concurrent: ▇▇▇▇  62.00
when:       ▇▇▇▇▇▇▇ 103.00
avow:       ▇▇▇▇▇▇▇▇▇ 142.00
deferred:   ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 424.00

==========================================================
Test: defer-reject x 10000
----------------------------------------------------------
avow:       ▇▇▇  50.00
concurrent: ▇▇▇▇▇  80.00
when:       ▇▇▇▇▇▇▇▇▇▇ 160.00
laissez:    ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 240.00
q:          ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 378.00

==========================================================
Test: defer-sequence x 10000
----------------------------------------------------------
laissez:    |   7.00
concurrent: ▇▇▇▇▇▇▇▇▇▇▇ 176.00
when:       ▇▇▇▇▇▇▇▇▇▇▇▇▇ 209.00
deferred:   ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 271.00
avow:       ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 352.00

==========================================================
Test: map x 10000
----------------------------------------------------------
deferred:   ▇▇▇▇▇  39.00
concurrent: ▇▇▇▇▇▇▇▇▇▇▇▇▇ 103.00
when:       ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 385.00

==========================================================
Test: reduce-large x 10000
NOTE: in node v0.8.14, deferred.reduce causes a
stack overflow for an array length >= 610
----------------------------------------------------------
concurrent: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 371.00
when:       ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 502.00
```

You can find more performance results [here](https://github.com/pspeter3/promise-perf-tests)

Overview
--------

### Simple Promise

Concurrent supports the bare bones Promise implementation that supports
`then(onFulfilled, onRejected)`, `fulfill(value)`, `reject(reason)`.

```js
var Promise = require('concurrent').Promise;

var success = new Promise();
success.then(function(value) {
  console.log(value); // 'success'
});
success.fulfill('success');

var failure = new Promise();
failure.then(null, function(reason) {
  console.log(reason); // 'failure'
});
failure.reject('failure');
```

[Documentation](http://pspeter3.com/concurrent/promise.js.html)

### Futures

Concurrent also provides a Future class which inherits from Promise. It has a
lot of syntactic sugar on top of the Promises/A+ spec based on the Scala Future
API.

```js
var Future = require('concurrent').Future;

var success = new Future();
success.onComplete(function(result) {
  console.log(result; // 'success'
});
success.fulfill('success');

var failure = new Future();
failure.onComplete(function(result) {
  console.log(result); // 'failure'
});
failure.reject('failure');
```

[Documentation](http://pspeter3.com/concurrent/future.js.html)

### Collections

Concurrent also provides a collections library which gives a lot of the standard
iterators. All the iterators are performed asynchronously and return Futures.
The following methods are supported:

- `forEach`
- `every`
- `some`
- `filter`
- `map`
- `reverse`
- `reduce`
- `reduceRight`

[Documentation](http://pspeter3.com/concurrent/collections.js.html)

### Working with existing callbacks

Futures also have support for working with existing callback style libraries by
using the `convert` method which returns a callback handler.

```js
var Future = require('concurrent').Future;
var request = require('request');

var google = new Future();
google.map(function(value) {
  var body = value[1]; // Request returns a response and a body
  console.log(body); // HTML for http://www.google.com
});
request('http://www.google.com', google.convert());
```

### Working with other Promise implementations

Since concurrent implements the Promises/A+ spec, it should work with other
libraries that implement the spec. Also, the Future class internally does not
expect any method beyond `then`, `fulfill`, and `reject` so the prototype
methods can be merged into other implementations as long as they have those
three methods.

Browsers
--------

Concurrent can be used in browser environments that support ES5, specifically
`forEach`, `Array.isArray` and `Object.create`. Look at this [JsFiddle](http://jsfiddle.net/pspeter3/h3MLs/)
as an example of using the libary in the browser.

Credits
-------

A lot of people had a hand in inspiring this project and helping getting it done. I'd like to thank:

- [@brikis98](https://github.com/brikis98) for helping me come up with the idea
- [Promises, understanding by doing](http://modernjavascript.blogspot.com/2013/08/promisesa-understanding-by-doing.html) for the initial promise spec
- [cujos/when](https://github.com/cujojs/when) for fully featured examples
- [aheckmann/mpromise](https://github.com/aheckmann/mpromise) for node.js specific implementation
- [promises-aplus/promises-tests](https://github.com/promises-aplus/promises-tests) for the test suite
- [Scala Futures](http://www.scala-lang.org/api/current/index.html#scala.concurrent.Future) For API sugar

License
-------

This is licensed under the MIT license. See the LICENSE file
