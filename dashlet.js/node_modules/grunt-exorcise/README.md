# grunt-exorcise [![Travis CI](https://travis-ci.org/mikefrey/grunt-exorcise.svg)](https://travis-ci.org/mikefrey/grunt-exorcise)

> Move Browserify source maps to a separate file using Exorcist and Grunt

## Getting Started
This plugin requires Grunt `0.4.x`

If you haven't used [Grunt](http://gruntjs.com/) before, be sure to check out the [Getting Started](http://gruntjs.com/getting-started) guide, as it explains how to create a [Gruntfile](http://gruntjs.com/sample-gruntfile) as well as install and use Grunt plugins. Once you're familiar with that process, you may install this plugin with this command:

```shell
npm install grunt-exorcise --save-dev
```

Once the plugin has been installed, it may be enabled inside your Gruntfile with this line of JavaScript:

```js
grunt.loadNpmTasks('grunt-exorcise');
```

## The "exorcise" task

```js
grunt.initConfig({
  exorcise: {
    bundle: {
      options: {},
      files: {
        'public/js/bundle.map': ['public/js/bundle.js'],
      }
    }
  }
});
```

### Options

#### options.bundleDest
Type: `String`

Location to place the new bundle with the inline source map removed. By default the source bundle file will be overwritten.

#### options.strict
Type: `Boolean`
Default: `false`
Fail the build when the source map is missing. Default is `false`, equivalent to exorcist default behaviour.

#### options.url & options.root & options.base
Type: `String`

Passed directly to exorcist. Refer to the exorcist [documentation](https://github.com/thlorenz/exorcist).

## Contributing
In lieu of a formal styleguide, take care to maintain the existing coding style. Add unit tests for any new or changed functionality. Lint and test your code using [Grunt](http://gruntjs.com/).

## Release History

### v0.1.0
  - Initial release
