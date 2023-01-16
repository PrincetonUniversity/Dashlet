"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
intern.registerLoader(function (options) {
    var globalObj = typeof window !== 'undefined' ? window : global;
    var _a = options.internLoaderPath, internLoaderPath = _a === void 0 ? 'node_modules/dojo/dojo.js' : _a, loaderConfig = __rest(options, ["internLoaderPath"]);
    loaderConfig.baseUrl = loaderConfig.baseUrl || intern.config.basePath;
    if (!('async' in loaderConfig)) {
        loaderConfig.async = true;
    }
    loaderConfig.has = __assign({ 'dojo-timeout-api': true }, loaderConfig.has);
    intern.log('Configuring Dojo loader with:', loaderConfig);
    globalObj.dojoConfig = loaderConfig;
    return intern.loadScript(internLoaderPath).then(function () {
        var require = globalObj.require;
        intern.log('Using Dojo loader');
        return function (modules) {
            var handle;
            return new Promise(function (resolve, reject) {
                handle = require.on('error', function (error) {
                    intern.emit('error', error);
                    reject(new Error("Dojo loader error: " + error.message));
                });
                intern.log('Loading modules:', modules);
                require(modules, function () {
                    resolve();
                });
            }).then(function () {
                handle.remove();
            }, function (error) {
                handle && handle.remove();
                throw error;
            });
        };
    });
});
//# sourceMappingURL=dojo.js.map