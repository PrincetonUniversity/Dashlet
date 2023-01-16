'use strict';

var grunt = require('grunt');

/*
  ======== A Handy Little Nodeunit Reference ========
  https://github.com/caolan/nodeunit

  Test methods:
    test.expect(numAssertions)
    test.done()
  Test assertions:
    test.ok(value, [message])
    test.equal(actual, expected, [message])
    test.notEqual(actual, expected, [message])
    test.deepEqual(actual, expected, [message])
    test.notDeepEqual(actual, expected, [message])
    test.strictEqual(actual, expected, [message])
    test.notStrictEqual(actual, expected, [message])
    test.throws(block, [error], [message])
    test.doesNotThrow(block, [error], [message])
    test.ifError(value)
*/

exports.exorcise = {
  bundle: function(test) {
    test.expect(1)

    var actual = grunt.file.read('tmp/map/bundle.js')
    var expected = grunt.file.read('test/expected/bundle.js')
    test.equal(actual, expected, 'should be rewritten with source map url instead of inlined')

    test.done()
  },
  map: function(test) {
    test.expect(2)

    test.ok(grunt.file.exists('tmp/map/bundle.map'), 'should exist')

    var actual = grunt.file.read('tmp/map/bundle.map')
    var expected = grunt.file.read('test/expected/bundle.map')
    test.equal(actual, expected, 'should be correct')

    test.done()
  },
  noMap: function(test) {
    test.expect(3)

    test.ok(grunt.file.exists('tmp/nomap/bundle.js'), 'should exist')
    test.ok(!grunt.file.exists('tmp/nomap/bundle.nomap'), 'should not exist')

    var actual = grunt.file.read('tmp/nomap/bundle.js')
    var expected = grunt.file.read('test/fixtures/bundle.nomap.js')
    test.equal(actual, expected, 'should be correct')

    test.done()
  }
}
