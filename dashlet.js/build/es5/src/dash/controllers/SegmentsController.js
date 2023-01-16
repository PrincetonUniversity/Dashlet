'use strict';Object.defineProperty(exports,"__esModule",{value:true});var _FactoryMaker=require('../../core/FactoryMaker');var _FactoryMaker2=_interopRequireDefault(_FactoryMaker);var _TimelineSegmentsGetter=require('../utils/TimelineSegmentsGetter');var _TimelineSegmentsGetter2=_interopRequireDefault(_TimelineSegmentsGetter);var _TemplateSegmentsGetter=require('../utils/TemplateSegmentsGetter');var _TemplateSegmentsGetter2=_interopRequireDefault(_TemplateSegmentsGetter);var _ListSegmentsGetter=require('../utils/ListSegmentsGetter');var _ListSegmentsGetter2=_interopRequireDefault(_ListSegmentsGetter);var _SegmentBaseGetter=require('../utils/SegmentBaseGetter');var _SegmentBaseGetter2=_interopRequireDefault(_SegmentBaseGetter);function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj};}function SegmentsController(config){config=config||{};var context=this.context;var events=config.events;var eventBus=config.eventBus;var dashConstants=config.dashConstants;var instance=void 0,getters=void 0;function setup(){getters={};}function initialize(isDynamic){getters[dashConstants.SEGMENT_TIMELINE]=(0,_TimelineSegmentsGetter2.default)(context).create(config,isDynamic);getters[dashConstants.SEGMENT_TEMPLATE]=(0,_TemplateSegmentsGetter2.default)(context).create(config,isDynamic);getters[dashConstants.SEGMENT_LIST]=(0,_ListSegmentsGetter2.default)(context).create(config,isDynamic);getters[dashConstants.SEGMENT_BASE]=(0,_SegmentBaseGetter2.default)(context).create(config,isDynamic);}function update(voRepresentation,type,mimeType,hasInitialization,hasSegments){if(!hasInitialization){eventBus.trigger(events.SEGMENTBASE_INIT_REQUEST_NEEDED,{mimeType:mimeType,representation:voRepresentation});}if(!hasSegments){eventBus.trigger(events.SEGMENTBASE_SEGMENTSLIST_REQUEST_NEEDED,{mimeType:mimeType,mediaType:type,representation:voRepresentation});}}function getSegmentsGetter(representation){return representation?representation.segments?getters[dashConstants.SEGMENT_BASE]:getters[representation.segmentInfoType]:null;}function getSegmentByIndex(representation,index,lastSegmentTime){var getter=getSegmentsGetter(representation);return getter?getter.getSegmentByIndex(representation,index,lastSegmentTime):null;}function getSegmentByTime(representation,time){var getter=getSegmentsGetter(representation);return getter?getter.getSegmentByTime(representation,time):null;}instance={initialize:initialize,update:update,getSegmentByIndex:getSegmentByIndex,getSegmentByTime:getSegmentByTime};setup();return instance;}/**
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
 */SegmentsController.__dashjs_factory_name='SegmentsController';var factory=_FactoryMaker2.default.getClassFactory(SegmentsController);exports.default=factory;
//# sourceMappingURL=SegmentsController.js.map
