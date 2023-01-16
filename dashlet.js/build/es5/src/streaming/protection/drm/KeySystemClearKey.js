'use strict';Object.defineProperty(exports,"__esModule",{value:true});var _KeyPair=require('../vo/KeyPair');var _KeyPair2=_interopRequireDefault(_KeyPair);var _ClearKeyKeySet=require('../vo/ClearKeyKeySet');var _ClearKeyKeySet2=_interopRequireDefault(_ClearKeyKeySet);var _CommonEncryption=require('../CommonEncryption');var _CommonEncryption2=_interopRequireDefault(_CommonEncryption);var _ProtectionConstants=require('../../constants/ProtectionConstants');var _ProtectionConstants2=_interopRequireDefault(_ProtectionConstants);function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj};}/**
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
 */var uuid='e2719d58-a985-b3c9-781a-b030af78d30e';var systemString=_ProtectionConstants2.default.CLEARKEY_KEYSTEM_STRING;var schemeIdURI='urn:uuid:'+uuid;function KeySystemClearKey(config){config=config||{};var instance=void 0;var BASE64=config.BASE64;var LICENSE_SERVER_MANIFEST_CONFIGURATIONS={attributes:['Laurl','laurl'],prefixes:['clearkey','dashif']};/**
     * Returns desired clearkeys (as specified in the CDM message) from protection data
     *
     * @param {ProtectionData} protectionData the protection data
     * @param {ArrayBuffer} message the ClearKey CDM message
     * @returns {ClearKeyKeySet} the key set or null if none found
     * @throws {Error} if a keyID specified in the CDM message was not found in the
     * protection data
     * @memberof KeySystemClearKey
     */function getClearKeysFromProtectionData(protectionData,message){var clearkeySet=null;if(protectionData){// ClearKey is the only system that does not require a license server URL, so we
// handle it here when keys are specified in protection data
var jsonMsg=JSON.parse(String.fromCharCode.apply(null,new Uint8Array(message)));var keyPairs=[];for(var i=0;i<jsonMsg.kids.length;i++){var clearkeyID=jsonMsg.kids[i];var clearkey=protectionData.clearkeys&&protectionData.clearkeys.hasOwnProperty(clearkeyID)?protectionData.clearkeys[clearkeyID]:null;if(!clearkey){throw new Error('DRM: ClearKey keyID ('+clearkeyID+') is not known!');}// KeyIDs from CDM are not base64 padded.  Keys may or may not be padded
keyPairs.push(new _KeyPair2.default(clearkeyID,clearkey));}clearkeySet=new _ClearKeyKeySet2.default(keyPairs);}return clearkeySet;}function getInitData(cp,cencContentProtection){try{var initData=_CommonEncryption2.default.parseInitDataFromContentProtection(cp,BASE64);if(!initData&&cencContentProtection){var cencDefaultKid=cencDefaultKidToBase64Representation(cencContentProtection['cenc:default_KID']);var data={kids:[cencDefaultKid]};initData=new TextEncoder().encode(JSON.stringify(data));}return initData;}catch(e){return null;}}function cencDefaultKidToBase64Representation(cencDefaultKid){try{var kid=cencDefaultKid.replace(/-/g,'');kid=btoa(kid.match(/\w{2}/g).map(function(a){return String.fromCharCode(parseInt(a,16));}).join(''));return kid.replace(/=/g,'');}catch(e){return null;}}function getRequestHeadersFromMessage()/*message*/{// Set content type to application/json by default
return{'Content-Type':'application/json'};}function getLicenseRequestFromMessage(message){return JSON.parse(String.fromCharCode.apply(null,new Uint8Array(message)));}function getLicenseServerURLFromInitData()/*initData*/{return null;}function getLicenseServerUrlFromMediaInfo(mediaInfo){try{if(!mediaInfo||mediaInfo.length===0){return null;}var i=0;var licenseServer=null;while(i<mediaInfo.length&&!licenseServer){var info=mediaInfo[i];if(info&&info.contentProtection&&info.contentProtection.length>0){var clearkeyProtData=info.contentProtection.filter(function(cp){return cp.schemeIdUri&&cp.schemeIdUri===schemeIdURI;});if(clearkeyProtData&&clearkeyProtData.length>0){var j=0;while(j<clearkeyProtData.length&&!licenseServer){var ckData=clearkeyProtData[j];var k=0;while(k<LICENSE_SERVER_MANIFEST_CONFIGURATIONS.attributes.length&&!licenseServer){var l=0;var attribute=LICENSE_SERVER_MANIFEST_CONFIGURATIONS.attributes[k];while(l<LICENSE_SERVER_MANIFEST_CONFIGURATIONS.prefixes.length&&!licenseServer){var prefix=LICENSE_SERVER_MANIFEST_CONFIGURATIONS.prefixes[l];if(ckData[attribute]&&ckData[attribute].__prefix&&ckData[attribute].__prefix===prefix&&ckData[attribute].__text){licenseServer=ckData[attribute].__text;}l+=1;}k+=1;}j+=1;}}}i+=1;}return licenseServer;}catch(e){return null;}}function getCDMData(){return null;}function getSessionId()/*cp*/{return null;}instance={uuid:uuid,schemeIdURI:schemeIdURI,systemString:systemString,getInitData:getInitData,getRequestHeadersFromMessage:getRequestHeadersFromMessage,getLicenseRequestFromMessage:getLicenseRequestFromMessage,getLicenseServerURLFromInitData:getLicenseServerURLFromInitData,getCDMData:getCDMData,getSessionId:getSessionId,getLicenseServerUrlFromMediaInfo:getLicenseServerUrlFromMediaInfo,getClearKeysFromProtectionData:getClearKeysFromProtectionData};return instance;}KeySystemClearKey.__dashjs_factory_name='KeySystemClearKey';exports.default=dashjs.FactoryMaker.getSingletonFactory(KeySystemClearKey);/* jshint ignore:line */
//# sourceMappingURL=KeySystemClearKey.js.map
