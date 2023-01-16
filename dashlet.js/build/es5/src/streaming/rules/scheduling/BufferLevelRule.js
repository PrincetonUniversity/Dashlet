'use strict';Object.defineProperty(exports,"__esModule",{value:true});var _Constants=require('../../constants/Constants');var _Constants2=_interopRequireDefault(_Constants);var _FactoryMaker=require('../../../core/FactoryMaker');var _FactoryMaker2=_interopRequireDefault(_FactoryMaker);var _MetricsConstants=require('../../constants/MetricsConstants');var _MetricsConstants2=_interopRequireDefault(_MetricsConstants);function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj};}function BufferLevelRule(config){config=config||{};var dashMetrics=config.dashMetrics;var mediaPlayerModel=config.mediaPlayerModel;var textController=config.textController;var abrController=config.abrController;var settings=config.settings;function setup(){}function execute(type,representationInfo){if(!type||!representationInfo){return true;}var bufferLevel=dashMetrics.getCurrentBufferLevel(type);return bufferLevel<getBufferTarget(type,representationInfo);}function getBufferTarget(type,representationInfo){var bufferTarget=NaN;if(!type||!representationInfo){return bufferTarget;}if(type===_Constants2.default.FRAGMENTED_TEXT){if(textController.isTextEnabled()){if(isNaN(representationInfo.fragmentDuration)){//fragmentDuration of representationInfo is not defined,
// call metrics function to have data in the latest scheduling info...
// if no metric, returns 0. In this case, rule will return false.
var schedulingInfo=dashMetrics.getCurrentSchedulingInfo(_MetricsConstants2.default.SCHEDULING_INFO);bufferTarget=schedulingInfo?schedulingInfo.duration:0;}else{bufferTarget=representationInfo.fragmentDuration;}}else{// text is disabled, rule will return false
bufferTarget=0;}}else{var streamInfo=representationInfo.mediaInfo.streamInfo;if(abrController.isPlayingAtTopQuality(streamInfo)){var isLongFormContent=streamInfo.manifestInfo.duration>=settings.get().streaming.longFormContentDurationThreshold;bufferTarget=isLongFormContent?settings.get().streaming.bufferTimeAtTopQualityLongForm:settings.get().streaming.bufferTimeAtTopQuality;}else{bufferTarget=mediaPlayerModel.getStableBufferTime();}}return bufferTarget;}var instance={execute:execute,getBufferTarget:getBufferTarget};setup();return instance;}/**
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
 */BufferLevelRule.__dashjs_factory_name='BufferLevelRule';exports.default=_FactoryMaker2.default.getClassFactory(BufferLevelRule);
//# sourceMappingURL=BufferLevelRule.js.map
