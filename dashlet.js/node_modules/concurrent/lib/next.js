/**
 * Executes a function asynchronously. Prefers setImmediate but will fallback to
 * process.nextTick for older versions of node.
 *
 * @type {Function}
 * @private
 */
var next = typeof setImmediate === 'function' ? setImmediate : process.nextTick;
module.exports = next;
