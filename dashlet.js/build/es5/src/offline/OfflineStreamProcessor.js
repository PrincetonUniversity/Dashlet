'use strict';Object.defineProperty(exports,"__esModule",{value:true});var _DashHandler=require('../dash/DashHandler');var _DashHandler2=_interopRequireDefault(_DashHandler);var _RepresentationController=require('../dash/controllers/RepresentationController');var _RepresentationController2=_interopRequireDefault(_RepresentationController);var _FragmentModel=require('../streaming/models/FragmentModel');var _FragmentModel2=_interopRequireDefault(_FragmentModel);var _FragmentLoader=require('../streaming/FragmentLoader');var _FragmentLoader2=_interopRequireDefault(_FragmentLoader);var _URLUtils=require('../streaming/utils/URLUtils');var _URLUtils2=_interopRequireDefault(_URLUtils);var _RequestModifier=require('../streaming/utils/RequestModifier');var _RequestModifier2=_interopRequireDefault(_RequestModifier);function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj};}/**
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
 */function OfflineStreamProcessor(config){config=config||{};var context=this.context;var eventBus=config.eventBus;var events=config.events;var errors=config.errors;var debug=config.debug;var constants=config.constants;var settings=config.settings;var dashConstants=config.dashConstants;var manifestId=config.id;var type=config.type;var streamInfo=config.streamInfo;var errHandler=config.errHandler;var mediaPlayerModel=config.mediaPlayerModel;var abrController=config.abrController;var playbackController=config.playbackController;var adapter=config.adapter;var dashMetrics=config.dashMetrics;var baseURLController=config.baseURLController;var timelineConverter=config.timelineConverter;var bitrate=config.bitrate;var offlineStoreController=config.offlineStoreController;var completedCb=config.callbacks&&config.callbacks.completed;var progressCb=config.callbacks&&config.callbacks.progression;var instance=void 0,logger=void 0,mediaInfo=void 0,indexHandler=void 0,representationController=void 0,fragmentModel=void 0,updating=void 0,downloadedSegments=void 0,isInitialized=void 0,isStopped=void 0;function setup(){resetInitialSettings();logger=debug.getLogger(instance);indexHandler=(0,_DashHandler2.default)(context).create({streamInfo:streamInfo,type:type,timelineConverter:timelineConverter,dashMetrics:dashMetrics,mediaPlayerModel:mediaPlayerModel,baseURLController:baseURLController,errHandler:errHandler,settings:settings,// boxParser: boxParser,
eventBus:eventBus,events:events,debug:debug,requestModifier:(0,_RequestModifier2.default)(context).getInstance(),dashConstants:dashConstants,constants:constants,urlUtils:(0,_URLUtils2.default)(context).getInstance()});representationController=(0,_RepresentationController2.default)(context).create({streamId:streamInfo.id,type:type,abrController:abrController,dashMetrics:dashMetrics,playbackController:playbackController,timelineConverter:timelineConverter,dashConstants:dashConstants,events:events,eventBus:eventBus,errors:errors});fragmentModel=(0,_FragmentModel2.default)(context).create({streamId:streamInfo.id,dashMetrics:dashMetrics,fragmentLoader:(0,_FragmentLoader2.default)(context).create({dashMetrics:dashMetrics,mediaPlayerModel:mediaPlayerModel,errHandler:errHandler,requestModifier:(0,_RequestModifier2.default)(context).getInstance(),settings:settings,eventBus:eventBus,events:events,errors:errors,constants:constants,dashConstants:dashConstants,urlUtils:(0,_URLUtils2.default)(context).getInstance()}),debug:debug,eventBus:eventBus,events:events});eventBus.on(events.STREAM_COMPLETED,onStreamCompleted,instance);eventBus.on(events.FRAGMENT_LOADING_COMPLETED,onFragmentLoadingCompleted,instance);}function initialize(_mediaInfo){mediaInfo=_mediaInfo;indexHandler.initialize(false);updateRepresentation(mediaInfo);}function isInitRequest(request){return request.type==='InitializationSegment';}function onFragmentLoadingCompleted(e){if(e.sender!==fragmentModel){return;}if(e.request!==null){var isInit=isInitRequest(e.request);var suffix=isInit?'init':e.request.index;var fragmentName=e.request.representationId+'_'+suffix;offlineStoreController.storeFragment(manifestId,fragmentName,e.response).then(function(){if(!isInit){// store current index and downloadedSegments number
offlineStoreController.setRepresentationCurrentState(manifestId,e.request.representationId,{index:e.request.index,downloaded:downloadedSegments});}});}if(e.error&&e.request.serviceLocation&&!isStopped){fragmentModel.executeRequest(e.request);}else{downloadedSegments++;download();}}function onStreamCompleted(e){if(e.fragmentModel!==fragmentModel){return;}logger.info('['+manifestId+'] Stream is complete');stop();completedCb();}function getRepresentationController(){return representationController;}function getRepresentationId(){return representationController.getCurrentRepresentation().id;}/**
     * Stops download of fragments
     * @memberof OfflineStreamProcessor#
     */function stop(){if(isStopped){return;}isStopped=true;}function removeExecutedRequestsBeforeTime(time){if(fragmentModel){fragmentModel.removeExecutedRequestsBeforeTime(time);}}/**
     * Execute init request for the represenation
     * @memberof OfflineStreamProcessor#
    */function getInitRequest(){if(!representationController.getCurrentRepresentation()){return null;}return indexHandler.getInitRequest(getMediaInfo(),representationController.getCurrentRepresentation());}/**
     * Get next request
     * @memberof OfflineStreamProcessor#
    */function getNextRequest(){return indexHandler.getNextSegmentRequest(getMediaInfo(),representationController.getCurrentRepresentation());}/**
     * Start download
     * @memberof OfflineStreamProcessor#
    */function start(){if(representationController){if(!representationController.getCurrentRepresentation()){throw new Error('Start denied to OfflineStreamProcessor');}isStopped=false;offlineStoreController.getRepresentationCurrentState(manifestId,representationController.getCurrentRepresentation().id).then(function(state){if(state){indexHandler.setCurrentIndex(state.index);downloadedSegments=state.downloaded;}download();}).catch(function(){// start from beginining
download();});}}/**
     * Performs download of fragment according to type
     * @memberof OfflineStreamProcessor#
    */function download(){if(isStopped){return;}if(isNaN(representationController.getCurrentRepresentation())){var request=null;if(!isInitialized){request=getInitRequest();isInitialized=true;}else{request=getNextRequest();// update progression : done here because availableSegmentsNumber is done in getNextRequest from dash handler
updateProgression();}if(request){logger.info('['+manifestId+'] download request : '+request.url);fragmentModel.executeRequest(request);}else{logger.info('['+manifestId+'] no request to be downloaded');}}}/**
     * Update representation
     * @param {Object} mediaInfo - mediaInfo
     * @memberof OfflineStreamProcessor#
     */function updateRepresentation(mediaInfo){updating=true;var voRepresentations=adapter.getVoRepresentations(mediaInfo);// get representation VO according to id.
var quality=voRepresentations.findIndex(function(representation){return representation.id===bitrate.id;});if(type!==constants.VIDEO&&type!==constants.AUDIO&&type!==constants.TEXT&&type!==constants.FRAGMENTED_TEXT){updating=false;return;}representationController.updateData(null,voRepresentations,type,quality);}function isUpdating(){return updating;}function getType(){return type;}function getMediaInfo(){return mediaInfo;}function getAvailableSegmentsNumber(){return representationController.getCurrentRepresentation().availableSegmentsNumber+1;// do not forget init segment
}function updateProgression(){if(progressCb){progressCb(instance,downloadedSegments,getAvailableSegmentsNumber());}}function resetInitialSettings(){isInitialized=false;downloadedSegments=0;updating=false;}/**
     * Reset
     * @memberof OfflineStreamProcessor#
    */function reset(){resetInitialSettings();indexHandler.reset();eventBus.off(events.STREAM_COMPLETED,onStreamCompleted,instance);eventBus.off(events.FRAGMENT_LOADING_COMPLETED,onFragmentLoadingCompleted,instance);}instance={initialize:initialize,getMediaInfo:getMediaInfo,getRepresentationController:getRepresentationController,removeExecutedRequestsBeforeTime:removeExecutedRequestsBeforeTime,getType:getType,getRepresentationId:getRepresentationId,isUpdating:isUpdating,start:start,stop:stop,getAvailableSegmentsNumber:getAvailableSegmentsNumber,reset:reset};setup();return instance;}OfflineStreamProcessor.__dashjs_factory_name='OfflineStreamProcessor';var factory=dashjs.FactoryMaker.getClassFactory(OfflineStreamProcessor);/* jshint ignore:line */exports.default=factory;
//# sourceMappingURL=OfflineStreamProcessor.js.map
