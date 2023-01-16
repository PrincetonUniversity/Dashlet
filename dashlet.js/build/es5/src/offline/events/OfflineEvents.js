'use strict';Object.defineProperty(exports,"__esModule",{value:true});var _EventsBase2=require('./../../core/events/EventsBase');var _EventsBase3=_interopRequireDefault(_EventsBase2);function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj};}function _classCallCheck(instance,Constructor){if(!(instance instanceof Constructor)){throw new TypeError("Cannot call a class as a function");}}function _possibleConstructorReturn(self,call){if(!self){throw new ReferenceError("this hasn't been initialised - super() hasn't been called");}return call&&(typeof call==="object"||typeof call==="function")?call:self;}function _inherits(subClass,superClass){if(typeof superClass!=="function"&&superClass!==null){throw new TypeError("Super expression must either be null or a function, not "+typeof superClass);}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,enumerable:false,writable:true,configurable:true}});if(superClass)Object.setPrototypeOf?Object.setPrototypeOf(subClass,superClass):subClass.__proto__=superClass;}/**
 * These are offline events that should be sent to the player level.
 * @class
 */var OfflineEvents=function(_EventsBase){_inherits(OfflineEvents,_EventsBase);function OfflineEvents(){_classCallCheck(this,OfflineEvents);/**
        * Triggered when all mediaInfo has been loaded
        * @event OfflineEvents#OFFLINE_RECORD_LOADEDMETADATA
        */var _this=_possibleConstructorReturn(this,(OfflineEvents.__proto__||Object.getPrototypeOf(OfflineEvents)).call(this));_this.OFFLINE_RECORD_LOADEDMETADATA='public_offlineRecordLoadedmetadata';/**
        * Triggered when a record is initialized and download is started
        * @event OfflineEvents#OFFLINE_RECORD_STARTED
        */_this.OFFLINE_RECORD_STARTED='public_offlineRecordStarted';/**
        * Triggered when the user stop downloading a record
        * @event OfflineEvents#OFFLINE_RECORD_STOPPED
        */_this.OFFLINE_RECORD_STOPPED='public_offlineRecordStopped';/**
        * Triggered when all record has been downloaded
        * @event OfflineEvents#OFFLINE_RECORD_FINISHED
        */_this.OFFLINE_RECORD_FINISHED='public_offlineRecordFinished';return _this;}return OfflineEvents;}(_EventsBase3.default);var offlineEvents=new OfflineEvents();exports.default=offlineEvents;
//# sourceMappingURL=OfflineEvents.js.map
