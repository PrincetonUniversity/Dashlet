"use strict";
intern.registerLoader(function (_config) {
    if (intern.environment !== 'browser') {
        throw new Error('The ESM loader only works in the browser');
    }
    intern.log('Using esm loader');
    var internBrowser = intern;
    return function (modules) {
        return internBrowser.loadScript(modules, true);
    };
});
//# sourceMappingURL=esm.js.map