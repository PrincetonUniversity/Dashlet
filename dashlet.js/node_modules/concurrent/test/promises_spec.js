var Promise = require('../lib/promise');
var aplus = require('promises-aplus-tests');

var adapter = {
  pending: function() {
    var promise = new Promise();
    return {
      promise: promise,
      fulfill: function(value) {
        promise.fulfill(value);
      },
      reject: function(reason) {
        promise.reject(reason);
      }
    };
  }
};

describe('Promises/A+ tests', function() {
  aplus.mocha(adapter);
});
