"use strict";
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
    var _a = options.internLoaderPath, internLoaderPath = _a === void 0 ? 'node_modules/@dojo/loader/loader.js' : _a, loaderConfig = __rest(options, ["internLoaderPath"]);
    return intern.loadScript(internLoaderPath).then(function () {
        var require = globalObj.require;
        intern.log('Using Dojo 2 loader');
        loaderConfig.baseUrl = loaderConfig.baseUrl || intern.config.basePath;
        intern.log('Configuring loader with:', loaderConfig);
        require.config(loaderConfig);
        return function (modules) {
            var handle;
            return new Promise(function (resolve, reject) {
                handle = require.on('error', function (error) {
                    intern.emit('error', error);
                    reject(error);
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
//# sourceMappingURL=dojo2.js.map