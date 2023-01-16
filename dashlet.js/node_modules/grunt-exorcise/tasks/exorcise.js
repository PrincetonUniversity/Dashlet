/*
 * grunt-exorcise
 * https://github.com/mikefrey/grunt-exorcise
 *
 * Copyright (c) 2014 Mike Frey
 * Licensed under the MIT license.
 */

'use strict';

var fs = require('fs')
var path = require('path')
var async = require('async')
var resumer = require('resumer')
var exorcist = require('exorcist')
var concat = require('concat-stream')

module.exports = function(grunt) {

  grunt.registerMultiTask('exorcise', 'Move Browserify source maps to a separate file', function() {
    var done = this.async()

    // Merge task-specific and/or target-specific options with these defaults.
    var options = this.options({
      url: null,
      root: null,
      base: null,
      strict: false
    });

    // Iterate over all specified file groups.
    async.eachSeries(this.files, function(file, cb) {
      if (!file.src || !file.src[0])
        return fail('Source file was not defined.', cb)
      if (!grunt.file.exists(file.src[0]))
        return fail('Source file "' + file.src[0].cyan + '" not found.', cb)

      var src = file.src[0]
      var dest = file.dest
      grunt.log.writeln('Exorcising source map from %s', src.cyan)

      // ensure that the dest directory exists
      grunt.file.mkdir(path.dirname(dest))

      // a bit of indirection happens here.
      // We can't stream the file directly through exorcist and
      // back to the file system without buffering it first because
      // we end up with an empty file streaming to exorcist.
      var data = fs.readFileSync(src, 'utf8')
      var stream = resumer().queue(data).end()
      var write = concat(function(data) {
        var out = options.bundleDest || src
        grunt.file.write(out, data)
        cb()
      })

      // setup exorcist
      var ex = exorcist(dest, options.url, options.root, options.base)
      ex.on('missing-map', function(msg) {
        grunt.log.warn(msg);
        if (options.strict)
          done(false)
      })

      stream.pipe(ex).pipe(write)
    }, done)
  })

  function fail(msg, cb) {
    grunt.log.warn(msg)
    throw new Error(msg)
  }

}
