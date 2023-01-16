"use strict";
intern.registerLoader(function (_config) {
    intern.log('Using default loader');
    return function (modules) {
        return intern.loadScript(modules);
    };
});
//# sourceMappingURL=default.js.map