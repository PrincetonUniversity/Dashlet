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
    var _a = options.internLoaderPath, internLoaderPath = _a === void 0 ? 'node_modules/systemjs/dist/system.src.js' : _a, loaderConfig = __rest(options, ["internLoaderPath"]);
    loaderConfig.baseURL = loaderConfig.baseURL || intern.config.basePath;
    if (intern.environment === 'browser') {
        return intern.loadScript(internLoaderPath).then(function () {
            return configAndLoad(SystemJS);
        });
    }
    else {
        var SystemJS_1 = (globalObj.require || require)('systemjs');
        return configAndLoad(SystemJS_1);
    }
    function configAndLoad(loader) {
        intern.log('Using SystemJS loader');
        intern.log('Configuring SystemJS with:', loaderConfig);
        loader.config(loaderConfig);
        return function (modules) {
            intern.log('Loading modules with SystemJS:', modules);
            return modules.reduce(function (previous, suite) {
                if (previous) {
                    return previous.then(function () { return loader.import(suite); });
                }
                return loader.import(suite);
            }, null);
        };
    }
});
//# sourceMappingURL=systemjs.js.map