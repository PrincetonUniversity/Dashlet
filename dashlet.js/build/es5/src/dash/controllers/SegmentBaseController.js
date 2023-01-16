'use strict';Object.defineProperty(exports,"__esModule",{value:true});var _FactoryMaker=require('../../core/FactoryMaker');var _FactoryMaker2=_interopRequireDefault(_FactoryMaker);var _SegmentBaseLoader=require('../SegmentBaseLoader');var _SegmentBaseLoader2=_interopRequireDefault(_SegmentBaseLoader);var _WebmSegmentBaseLoader=require('../WebmSegmentBaseLoader');var _WebmSegmentBaseLoader2=_interopRequireDefault(_WebmSegmentBaseLoader);function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj};}function SegmentBaseController(config){config=config||{};var context=this.context;var eventBus=config.eventBus;var events=config.events;var dashMetrics=config.dashMetrics;var mediaPlayerModel=config.mediaPlayerModel;var errHandler=config.errHandler;var baseURLController=config.baseURLController;var debug=config.debug;var boxParser=config.boxParser;var requestModifier=config.requestModifier;var errors=config.errors;var instance=void 0,segmentBaseLoader=void 0,webmSegmentBaseLoader=void 0;function setup(){segmentBaseLoader=(0,_SegmentBaseLoader2.default)(context).getInstance();webmSegmentBaseLoader=(0,_WebmSegmentBaseLoader2.default)(context).getInstance();segmentBaseLoader.setConfig({baseURLController:baseURLController,dashMetrics:dashMetrics,mediaPlayerModel:mediaPlayerModel,errHandler:errHandler,eventBus:eventBus,events:events,errors:errors,debug:debug,boxParser:boxParser,requestModifier:requestModifier});webmSegmentBaseLoader.setConfig({baseURLController:baseURLController,dashMetrics:dashMetrics,mediaPlayerModel:mediaPlayerModel,errHandler:errHandler,eventBus:eventBus,events:events,errors:errors,debug:debug,requestModifier:requestModifier});}function isWebM(mimeType){var type=mimeType?mimeType.split('/')[1]:'';return'webm'===type.toLowerCase();}function initialize(){eventBus.on(events.SEGMENTBASE_INIT_REQUEST_NEEDED,onInitSegmentBaseNeeded,instance);eventBus.on(events.SEGMENTBASE_SEGMENTSLIST_REQUEST_NEEDED,onSegmentsListSegmentBaseNeeded,instance);segmentBaseLoader.initialize();webmSegmentBaseLoader.initialize();}function onInitSegmentBaseNeeded(e){if(isWebM(e.mimeType)){webmSegmentBaseLoader.loadInitialization(e.representation);}else{segmentBaseLoader.loadInitialization(e.representation);}}function onSegmentsListSegmentBaseNeeded(e){if(isWebM(e.mimeType)){webmSegmentBaseLoader.loadSegments(e.representation,e.mediaType,e.representation?e.representation.indexRange:null,e.callback);}else{segmentBaseLoader.loadSegments(e.representation,e.mediaType,e.representation?e.representation.indexRange:null,e.callback);}}function reset(){eventBus.off(events.SEGMENTBASE_INIT_REQUEST_NEEDED,onInitSegmentBaseNeeded,instance);eventBus.off(events.SEGMENTBASE_SEGMENTSLIST_REQUEST_NEEDED,onSegmentsListSegmentBaseNeeded,instance);}instance={initialize:initialize,reset:reset};setup();return instance;}/**
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
 */SegmentBaseController.__dashjs_factory_name='SegmentBaseController';var factory=_FactoryMaker2.default.getSingletonFactory(SegmentBaseController);exports.default=factory;
//# sourceMappingURL=SegmentBaseController.js.map
