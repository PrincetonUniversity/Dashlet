'use strict';Object.defineProperty(exports,"__esModule",{value:true});var _FactoryMaker=require('../../core/FactoryMaker');var _FactoryMaker2=_interopRequireDefault(_FactoryMaker);var _Constants=require('../../streaming/constants/Constants');var _Constants2=_interopRequireDefault(_Constants);function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj};}/**
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
 */function SegmentBaseGetter(config){config=config||{};var timelineConverter=config.timelineConverter;var instance=void 0;function checkConfig(){if(!timelineConverter||!timelineConverter.hasOwnProperty('calcPeriodRelativeTimeFromMpdRelativeTime')){throw new Error(_Constants2.default.MISSING_CONFIG_ERROR);}}function getSegmentByIndex(representation,index){checkConfig();if(!representation){return null;}var len=representation.segments?representation.segments.length:-1;var seg=void 0;if(index<len){seg=representation.segments[index];if(seg&&seg.availabilityIdx===index){return seg;}}for(var i=0;i<len;i++){seg=representation.segments[i];if(seg&&seg.availabilityIdx===index){return seg;}}return null;}function getSegmentByTime(representation,requestedTime){checkConfig();var index=getIndexByTime(representation,requestedTime);return getSegmentByIndex(representation,index);}function getIndexByTime(representation,time){if(!representation){return-1;}var segments=representation.segments;var ln=segments?segments.length:null;var idx=-1;var epsilon=void 0,frag=void 0,ft=void 0,fd=void 0,i=void 0;if(segments&&ln>0){for(i=0;i<ln;i++){frag=segments[i];ft=frag.presentationStartTime;fd=frag.duration;epsilon=fd/2;if(time+epsilon>=ft&&time-epsilon<ft+fd){idx=frag.availabilityIdx;break;}}}return idx;}instance={getSegmentByIndex:getSegmentByIndex,getSegmentByTime:getSegmentByTime};return instance;}SegmentBaseGetter.__dashjs_factory_name='SegmentBaseGetter';var factory=_FactoryMaker2.default.getClassFactory(SegmentBaseGetter);exports.default=factory;
//# sourceMappingURL=SegmentBaseGetter.js.map
