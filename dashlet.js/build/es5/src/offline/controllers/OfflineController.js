'use strict';Object.defineProperty(exports,"__esModule",{value:true});var _OfflineConstants=require('../constants/OfflineConstants');var _OfflineConstants2=_interopRequireDefault(_OfflineConstants);var _OfflineStoreController=require('./OfflineStoreController');var _OfflineStoreController2=_interopRequireDefault(_OfflineStoreController);var _OfflineDownload=require('../OfflineDownload');var _OfflineDownload2=_interopRequireDefault(_OfflineDownload);var _IndexDBOfflineLoader=require('../net/IndexDBOfflineLoader');var _IndexDBOfflineLoader2=_interopRequireDefault(_IndexDBOfflineLoader);var _OfflineUrlUtils=require('../utils/OfflineUrlUtils');var _OfflineUrlUtils2=_interopRequireDefault(_OfflineUrlUtils);var _OfflineEvents=require('../events/OfflineEvents');var _OfflineEvents2=_interopRequireDefault(_OfflineEvents);var _OfflineErrors=require('../errors/OfflineErrors');var _OfflineErrors2=_interopRequireDefault(_OfflineErrors);var _OfflineDownloadVo=require('../vo/OfflineDownloadVo');var _OfflineDownloadVo2=_interopRequireDefault(_OfflineDownloadVo);function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj};}/**
 * @module OfflineController
 * @param {Object} config - dependencies
 * @description Provides access to offline stream recording and playback functionality.
 *//**
 * The copyright in this software is being made available under the BSD License,
 * included below. This software may be subject to other third party and contributor
 * rights, including patent rights, and no such rights are granted under this license.
 *
 * Copyright (c) 2013, Dash Industry Forum.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *  * Redistributions of source code must retain the above copyright notice, this
 *  list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright notice,
 *  this list of conditions and the following disclaimer in the documentation and/or
 *  other materials provided with the distribution.
 *  * Neither the name of Dash Industry Forum nor the names of its
 *  contributors may be used to endorse or promote products derived from this software
 *  without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS AS IS AND ANY
 *  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 *  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 *  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 *  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 *  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 *  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 *  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 *  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 */function OfflineController(config){var context=this.context;var errHandler=config.errHandler;var events=config.events;var errors=config.errors;var settings=config.settings;var eventBus=config.eventBus;var debug=config.debug;var manifestLoader=config.manifestLoader;var manifestModel=config.manifestModel;var mediaPlayerModel=config.mediaPlayerModel;var abrController=config.abrController;var playbackController=config.playbackController;var dashMetrics=config.dashMetrics;var timelineConverter=config.timelineConverter;var adapter=config.adapter;var manifestUpdater=config.manifestUpdater;var baseURLController=config.baseURLController;var schemeLoaderFactory=config.schemeLoaderFactory;var constants=config.constants;var dashConstants=config.dashConstants;var urlUtils=config.urlUtils;var instance=void 0,downloads=void 0,logger=void 0,offlineStoreController=void 0,offlineUrlUtils=void 0;function setup(){logger=debug.getLogger(instance);offlineStoreController=(0,_OfflineStoreController2.default)(context).create({eventBus:config.eventBus,errHandler:errHandler});offlineUrlUtils=(0,_OfflineUrlUtils2.default)(context).getInstance();urlUtils.registerUrlRegex(offlineUrlUtils.getRegex(),offlineUrlUtils);schemeLoaderFactory.registerLoader(_OfflineConstants2.default.OFFLINE_SCHEME,_IndexDBOfflineLoader2.default);downloads=[];}/*
    ---------------------------------------------------------------------------
        DOWNLOAD LIST FUNCTIONS
    ---------------------------------------------------------------------------
    */function getDownloadFromId(id){var download=downloads.find(function(item){return item.getId()===id;});return download;}function createDownloadFromId(id){var download=void 0;download=getDownloadFromId(id);if(!download){// create download controller
download=(0,_OfflineDownload2.default)(context).create({id:id,eventBus:eventBus,events:events,errors:errors,settings:settings,manifestLoader:manifestLoader,manifestModel:manifestModel,mediaPlayerModel:mediaPlayerModel,manifestUpdater:manifestUpdater,baseURLController:baseURLController,abrController:abrController,playbackController:playbackController,adapter:adapter,dashMetrics:dashMetrics,timelineConverter:timelineConverter,errHandler:errHandler,offlineStoreController:offlineStoreController,debug:debug,constants:constants,dashConstants:dashConstants,urlUtils:urlUtils});downloads.push(download);}return download;}function createDownloadFromStorage(offline){var download=getDownloadFromId(offline.manifestId);if(!download){download=createDownloadFromId(offline.manifestId);var status=offline.status;if(status===_OfflineConstants2.default.OFFLINE_STATUS_STARTED){status=_OfflineConstants2.default.OFFLINE_STATUS_STOPPED;}download.setInitialState({url:offline.url,progress:offline.progress,originalUrl:offline.originalURL,status:status});}return download;}function removeDownloadFromId(id){return new Promise(function(resolve,reject){var download=getDownloadFromId(id);var waitForStatusChanged=false;if(download){//is download running?
if(download.isDownloading()){//register status changed event
waitForStatusChanged=true;var downloadStopped=function downloadStopped(){eventBus.off(events.OFFLINE_RECORD_STOPPED,downloadStopped,instance);return offlineStoreController.deleteDownloadById(id).then(function(){resolve();}).catch(function(err){reject(err);});};eventBus.on(events.OFFLINE_RECORD_STOPPED,downloadStopped,instance);}download.deleteDownload();var index=downloads.indexOf(download);downloads.splice(index,1);}if(!waitForStatusChanged){resolve();}});}function generateManifestId(){var timestamp=new Date().getTime();return timestamp;}/*
    ---------------------------------------------------------------------------

        OFFLINE CONTROLLER API

    ---------------------------------------------------------------------------
    *//**
     * Loads records from storage
     * This methods has to be called first, to be sure that all downloads have been loaded
     *
     * @return {Promise} asynchronously resolved
     * @memberof module:OfflineController
     */function loadRecordsFromStorage(){return new Promise(function(resolve,reject){offlineStoreController.getAllManifests().then(function(items){items.manifests.forEach(function(offline){createDownloadFromStorage(offline);});resolve();}).catch(function(e){logger.error('Failed to load downloads '+e);reject(e);});});}/**
     * Get all records from storage
     *
     * @return {Promise} asynchronously resolved with records
     * @memberof module:OfflineController
     * @instance
     */function getAllRecords(){var records=[];downloads.forEach(function(download){var record=new _OfflineDownloadVo2.default();record.id=download.getId();record.progress=download.getDownloadProgression();record.url=download.getOfflineUrl();record.originalUrl=download.getManifestUrl();record.status=download.getStatus();records.push(record);});return records;}/**
     * Create a new content record in storage and download manifest from url
     *
     * @param {string} manifestURL - the content manifest url
     * @return {Promise} asynchronously resolved with record identifier
     * @memberof module:OfflineController
     * @instance
     */function createRecord(manifestURL){return new Promise(function(resolve,reject){var id=generateManifestId();// create download controller
var download=createDownloadFromId(id);download.downloadFromUrl(manifestURL).then(function(){download.initDownload();resolve(id);}).catch(function(e){logger.error('Failed to download '+e);removeDownloadFromId(id).then(function(){reject(e);});});});}/**
     * Start downloading the record with selected tracks representations
     *
     * @param {string} id - record identifier
     * @param {MediaInfo[]} mediaInfos - the selected tracks representations
     * @memberof module:OfflineController
     * @instance
     */function startRecord(id,mediaInfos){var download=getDownloadFromId(id);if(download){download.startDownload(mediaInfos);}}/**
     * Stop downloading of the record
     *
     * @param {string} id - record identifier
     * @memberof module:OfflineController
     * @instance
     */function stopRecord(id){var download=getDownloadFromId(id);if(download){download.stopDownload();}}/**
     * Resume downloading of the record
     *
     * @param {string} id - record identifier
     * @memberof module:OfflineController
     * @instance
     */function resumeRecord(id){var download=getDownloadFromId(id);if(download){download.resumeDownload();}}/**
     * Deletes a record from storage
     *
     * @param {string} id - record identifier
     * @memberof module:OfflineController
     * @instance
     */function deleteRecord(id){return removeDownloadFromId(id).then(function(){return offlineStoreController.deleteDownloadById(id);});}/**
     * Get download progression of a record
     *
     * @param {string} id - record identifier
     * @return {number} percentage progression
     * @memberof module:OfflineController
     * @instance
     */function getRecordProgression(id){var download=getDownloadFromId(id);if(download){return download.getDownloadProgression();}return 0;}/**
     * Reset all records
     * @memberof module:OfflineController
     * @instance
     */function resetRecords(){downloads.forEach(function(download){download.resetDownload();});}/**
     * Reset
     * @instance
     */function reset(){resetRecords();schemeLoaderFactory.unregisterLoader(_OfflineConstants2.default.OFFLINE_SCHEME);}instance={loadRecordsFromStorage:loadRecordsFromStorage,createRecord:createRecord,startRecord:startRecord,stopRecord:stopRecord,resumeRecord:resumeRecord,deleteRecord:deleteRecord,getRecordProgression:getRecordProgression,getAllRecords:getAllRecords,resetRecords:resetRecords,reset:reset};setup();return instance;}OfflineController.__dashjs_factory_name='OfflineController';var factory=dashjs.FactoryMaker.getClassFactory(OfflineController);/* jshint ignore:line */factory.events=_OfflineEvents2.default;factory.errors=_OfflineErrors2.default;dashjs.FactoryMaker.updateClassFactory(OfflineController.__dashjs_factory_name,factory);/* jshint ignore:line */exports.default=factory;
//# sourceMappingURL=OfflineController.js.map
