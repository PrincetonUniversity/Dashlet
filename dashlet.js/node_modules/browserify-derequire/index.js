/*
**  browserify-derequire -- Browserify Plugin for Renaming require() Calls
**  Copyright (c) 2015-2018 Ralf S. Engelschall <rse@engelschall.com>
**
**  Permission is hereby granted, free of charge, to any person obtaining
**  a copy of this software and associated documentation files (the
**  "Software"), to deal in the Software without restriction, including
**  without limitation the rights to use, copy, modify, merge, publish,
**  distribute, sublicense, and/or sell copies of the Software, and to
**  permit persons to whom the Software is furnished to do so, subject to
**  the following conditions:
**
**  The above copyright notice and this permission notice shall be included
**  in all copies or substantial portions of the Software.
**
**  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
**  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
**  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
**  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
**  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
**  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
**  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

var through   = require("through2");
var derequire = require("derequire");

/*  export a Browserify plugin  */
module.exports = function (browserify, opts) {
    /*  create a transform stream  */
    var createStream = function () {
        var code = "";
        var stream = through.obj(function (buf, enc, next) {
            /*  accumulate the code chunks  */
            code += buf.toString();
            next();
        }, function (next) {
            /*  transform the code  */
            if (opts.derequire === undefined)
                opts.derequire = [ { from: "require", to: "_dereq_" } ];
            code = derequire(code, opts.derequire);
            this.push(new Buffer(code));
            next();
        });
        stream.label = "derequire";
        return stream;
    };

    /*  hook into the bundle generation pipeline of Browserify  */
    browserify.pipeline.get("wrap").push(createStream());
    browserify.on("reset", function () {
        browserify.pipeline.get("wrap").push(createStream());
    });
};

