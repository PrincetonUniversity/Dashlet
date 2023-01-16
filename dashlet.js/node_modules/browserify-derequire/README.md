
browserify-derequire
====================

[Browserify](http://browserify.org/) plugin for renaming require() calls
in the output bundle.

<p/>
<img src="https://nodei.co/npm/browserify-derequire.png?downloads=true&stars=true" alt=""/>

<p/>
<img src="https://david-dm.org/rse/browserify-derequire.png" alt=""/>

About
-----

When creating Browser versions of libraries and applications with the
help of the excellent [Browserify](http://browserify.org/) toolchain,
even in `standalone` mode all
`require()` calls are left intact. This causes trouble on
subsequent embedding of the bundle (and this way reanalyzing) in other Browserify toolchains.
This Browserify plugin applies [derequire](https://www.npmjs.com/package/derequire)
in order to rename all `require()` calls to `_dereq_()` calls in the bundle output.

Installation
------------

```shell
$ npm install -g browserify
$ npm install -g browserify-derequire
```

Usage
-----

#### Shell

```shell
$ browserify -p browserify-derequire \
             -o sample.browser.js sample.js
```

#### Grunt

```js
module.exports = function (grunt) {
    grunt.loadNpmTasks("grunt-browserify");
    grunt.initConfig({
        browserify: {
            "sample": {
                files: {
                    "sample.browser.js": [ "sample.js" ]
                },
                options: {
                    plugin: [
                        [ "browserify-derequire" ]
                    ]
                }
            }
        },
        [...]
    });
    [...]
};
```

License
-------

Copyright (c) 2015-2018 Ralf S. Engelschall (http://engelschall.com/)

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

