/**
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
 */
import Constants from '../constants/Constants';
import MetricsConstants from '../constants/MetricsConstants';
import BufferLevelRule from '../rules/scheduling/BufferLevelRule';
import BufferQuota from '../rules/scheduling/BufferQuota';
import FragmentModel from '../models/FragmentModel';
import EventBus from '../../core/EventBus';
import Events from '../../core/events/Events';
import FactoryMaker from '../../core/FactoryMaker';
import Debug from '../../core/Debug';
import MediaController from './MediaController';

function ScheduleController(config) {

    config = config || {};
    const context = this.context;
    const eventBus = EventBus(context).getInstance();
    const adapter = config.adapter;
    const dashMetrics = config.dashMetrics;
    const mediaPlayerModel = config.mediaPlayerModel;
    const fragmentModel = config.fragmentModel;
    const abrController = config.abrController;
    const playbackController = config.playbackController;
    const textController = config.textController;
    const streamId = config.streamId;
    const type = config.type;
    const mimeType = config.mimeType;
    const mediaController = config.mediaController;
    const bufferController = config.bufferController;
    const settings = config.settings;

    let instance,
        logger,
        currentRepresentationInfo,
        initialRequest,
        isStopped,
        isFragmentProcessingInProgress,
        timeToLoadDelay,
        scheduleTimeout,
        seekTarget,
        hasVideoTrack,
        bufferLevelRule,
        lastFragmentRequest,
        topQualityIndex,
        lastInitQuality,
        replaceRequestArray,
        switchTrack,
        replacingBuffer,
        mediaRequest,
        checkPlaybackQuality,
        isReplacementRequest,
        bufferQuota;

    function setup() {
        logger = Debug(context).getInstance().getLogger(instance);
        resetInitialSettings();
    }

    function initialize(_hasVideoTrack) {
        hasVideoTrack = _hasVideoTrack;

        bufferLevelRule = BufferLevelRule(context).create({
            abrController: abrController,
            dashMetrics: dashMetrics,
            mediaPlayerModel: mediaPlayerModel,
            textController: textController,
            settings: settings
        });

        //eventBus.on(Events.LIVE_EDGE_SEARCH_COMPLETED, onLiveEdgeSearchCompleted, this);
        eventBus.on(Events.DATA_UPDATE_STARTED, onDataUpdateStarted, this);
        eventBus.on(Events.FRAGMENT_LOADING_COMPLETED, onFragmentLoadingCompleted, this);
        eventBus.on(Events.STREAM_COMPLETED, onStreamCompleted, this);
        eventBus.on(Events.BUFFER_CLEARED, onBufferCleared, this);
        eventBus.on(Events.BYTES_APPENDED_END_FRAGMENT, onBytesAppended, this);
        eventBus.on(Events.QUOTA_EXCEEDED, onQuotaExceeded, this);
        eventBus.on(Events.PLAYBACK_SEEKING, onPlaybackSeeking, this);
        eventBus.on(Events.PLAYBACK_STARTED, onPlaybackStarted, this);
        eventBus.on(Events.PLAYBACK_RATE_CHANGED, onPlaybackRateChanged, this);
        eventBus.on(Events.PLAYBACK_TIME_UPDATED, onPlaybackTimeUpdated, this);
        eventBus.on(Events.URL_RESOLUTION_FAILED, onURLResolutionFailed, this);
        eventBus.on(Events.FRAGMENT_LOADING_ABANDONED, onFragmentLoadingAbandoned, this);
        eventBus.on(Events.BUFFERING_COMPLETED, onBufferingCompleted, this);
        eventBus.on(Events.INITQUOTA, onInitQuota, this);
        // eventBus.on(Events.TESTEVENT, talert, this);


        eventBus.trigger(Events.INITQUOTAREQUEST);
        
    }

    function setCurrentRepresentation(representationInfo) {
        currentRepresentationInfo = representationInfo;
    }

    function isStarted() {
        return (isStopped === false);
    }

    function start() {
        // console.log('schedule controller start');
        if (isStarted()) return;
        if (!currentRepresentationInfo || bufferController.getIsBufferingCompleted()) return;

        logger.debug('Schedule Controller starts');
        isStopped = false;
        dashMetrics.createPlaylistTraceMetrics(currentRepresentationInfo.id, playbackController.getTime() * 1000, playbackController.getPlaybackRate());

        if (initialRequest) {
            initialRequest = false;
        }

        // console.log('schedule controller start2');
        
        startScheduleTimer(0);
    }

    function stop() {
        if (isStopped) return;

        logger.debug('Schedule Controller stops');
        logger.debug(type + ' Schedule Controller stops');
        isStopped = true;
        clearTimeout(scheduleTimeout);
    }

    function hasTopQualityChanged(type, id) {
        topQualityIndex[id] = topQualityIndex[id] || {};
        const newTopQualityIndex = abrController.getTopQualityIndexFor(type, id);

        if (topQualityIndex[id][type] != newTopQualityIndex) {
            logger.info('Top quality ' + type + ' index has changed from ' + topQualityIndex[id][type] + ' to ' + newTopQualityIndex);
            topQualityIndex[id][type] = newTopQualityIndex;
            return true;
        }
        return false;

    }

    // function talert() {
        // let status = bufferQuota.checkQuota();
        // alert('quota: '+status);
    // }

    function schedule() {

        if (isStopped || isFragmentProcessingInProgress ||
            (playbackController.isPaused() && !settings.get().streaming.scheduleWhilePaused) ||
            ((type === Constants.FRAGMENTED_TEXT || type === Constants.TEXT) && !textController.isTextEnabled()) ||
            bufferController.getIsBufferingCompleted()) {

            stop();
            return;
        }

        validateExecutedFragmentRequest();

        const isReplacement = replaceRequestArray.length > 0;
        
        // bufferLevelRule.execute(type, currentRepresentationInfo, hasVideoTrack) checks the buffer length
        if (replacingBuffer || isNaN(lastInitQuality) || switchTrack || isReplacement ||
            hasTopQualityChanged(type, streamId) ||
            bufferLevelRule.execute(type, currentRepresentationInfo, hasVideoTrack)) {

            const getNextFragment = function () {

                // var xhr = new XMLHttpRequest();
                // xhr.open("POST", "http://localhost:8333", false);
                // xhr.onreadystatechange = function() {
                //     if ( xhr.readyState == 4 && xhr.status == 200 ) {
                //         console.log("GOT RESPONSE:" + xhr.responseText + "---");
                //         // if ( xhr.responseText == "REFRESH" ) {
                //         //     document.location.reload(true);
                //         // }
                //     }
                // }
                // var data = {'nextChunkSize': 1, 'Type': 'BB', 'lastquality': 1, 'buffer': 5, 'bufferAdjusted': 5, 'bandwidthEst': 10, 'lastRequest': 1, 'RebufferTime': 1, 'lastChunkFinishTime': 1, 'lastChunkStartTime': 1, 'lastChunkSize': 1};
                // xhr.send(JSON.stringify(data));



                if ((currentRepresentationInfo.quality !== lastInitQuality || switchTrack) && (!replacingBuffer)) {
                    if (switchTrack) {
                        logger.debug('Switch track for ' + type + ', representation id = ' + currentRepresentationInfo.id);
                        replacingBuffer = mediaController.getSwitchMode(type) === MediaController.TRACK_SWITCH_MODE_ALWAYS_REPLACE;
                        if (replacingBuffer && bufferController.replaceBuffer) {
                            bufferController.replaceBuffer();
                        }
                        switchTrack = false;
                    } else {
                        logger.debug('Quality has changed, get init request for representationid = ' + currentRepresentationInfo.id);
                    }
                    eventBus.trigger(Events.INIT_FRAGMENT_NEEDED, {
                        sender: instance,
                        streamId: streamId,
                        mediaType: type,
                        representationId: currentRepresentationInfo.id
                    });
                    lastInitQuality = currentRepresentationInfo.quality;
                    checkPlaybackQuality = false;
                    // console.log("INIT_FRAGMENT_NEEDED1 >>>>> " + currentRepresentationInfo.quality);
                    
                    // currentRepresentationInfo
                    if (currentRepresentationInfo.mediaInfo.type == "video"){
                        console.log(currentRepresentationInfo);
                        console.log("[init] schedule1 " + currentRepresentationInfo.quality + " -- " + currentRepresentationInfo.mediaInfo.streamInfo.duration + " -- "  + abrController.getLastIndex());
                    }
                    
                } else {
                    const replacement = replaceRequestArray.shift();

                    if (replacement && replacement.isInitializationRequest()) {
                        // To be sure the specific init segment had not already been loaded
                        eventBus.trigger(Events.INIT_FRAGMENT_NEEDED, {
                            sender: instance,
                            streamId: streamId,
                            mediaType: type,
                            representationId: replacement.representationId
                        });
                        checkPlaybackQuality = false;
                        // console.log("INIT_FRAGMENT_NEEDED2 ");
                        if (currentRepresentationInfo.mediaInfo.type == "video"){
                            console.log("[init] schedule2 " + currentRepresentationInfo.quality);
                        }

                    } else {
                        eventBus.trigger(Events.MEDIA_FRAGMENT_NEEDED, {
                            sender: instance,
                            streamId: streamId,
                            mediaType: type,
                            seekTarget: seekTarget,
                            replacement: replacement
                        });
                        checkPlaybackQuality = true;

                        if (currentRepresentationInfo.mediaInfo.type == "video"){
                            console.log(currentRepresentationInfo);
                            // console.log()
                            console.log("[init] schedule3 " + currentRepresentationInfo.quality + " -- " + currentRepresentationInfo.mediaInfo.streamInfo.duration + " -- "  + abrController.getLastIndex());
                        }
                    }
                }
            };
            var ret = 0;
            setFragmentProcessState(true);
            // console.log("<<<<<<<<");
            // console.log("checkPlaybackQuality0");
            if (!isReplacement && checkPlaybackQuality) {
                // console.log("[buffer] " + bufferController.getRebufferTime());
                ret = abrController.checkPlaybackQuality(type, bufferController.getRebufferTime());
            }
            
            // if the return value means not buffer, sleep and do not buffer
            if (ret == -1) {
                setFragmentProcessState(false);
                startScheduleTimer(500);
            } else {
                getNextFragment();
            }

        } else {
            startScheduleTimer(500);
        }
    }

    function validateExecutedFragmentRequest() {
        // Validate that the fragment request executed and appended into the source buffer is as
        // good of quality as the current quality and is the correct media track.
        const time = playbackController.getTime();
        let safeBufferLevel = 1.5;

        if (isNaN(currentRepresentationInfo.fragmentDuration)) { //fragmentDuration of representationInfo is not defined,
            // call metrics function to have data in the latest scheduling info...
            // if no metric, returns 0. In this case, rule will return false.
            const schedulingInfo = dashMetrics.getCurrentSchedulingInfo(currentRepresentationInfo.mediaInfo.type);
            safeBufferLevel = schedulingInfo ? schedulingInfo.duration * 1.5 : 1.5;
        }
        const request = fragmentModel.getRequests({
            state: FragmentModel.FRAGMENT_MODEL_EXECUTED,
            time: time + safeBufferLevel,
            threshold: 0
        })[0];

        if (request && replaceRequestArray.indexOf(request) === -1 && !adapter.getIsTextTrack(mimeType)) {
            const fastSwitchModeEnabled = settings.get().streaming.fastSwitchEnabled;
            const bufferLevel = bufferController.getBufferLevel();
            const abandonmentState = abrController.getAbandonmentStateFor(type);

            // Only replace on track switch when NEVER_REPLACE
            const trackChanged = !mediaController.isCurrentTrack(request.mediaInfo) && mediaController.getSwitchMode(request.mediaInfo.type) === MediaController.TRACK_SWITCH_MODE_NEVER_REPLACE;
            const qualityChanged = request.quality < currentRepresentationInfo.quality;

            if (fastSwitchModeEnabled && (trackChanged || qualityChanged) && bufferLevel >= safeBufferLevel && abandonmentState !== MetricsConstants.ABANDON_LOAD) {
                replaceRequest(request);
                // console.log("replaceRequest - validateExecutedFragmentRequest")

                isReplacementRequest = true;
                logger.debug('Reloading outdated fragment at index: ', request.index);
            } else if (request.quality > currentRepresentationInfo.quality && !replacingBuffer) {
                // The buffer has better quality it in then what we would request so set append point to end of buffer!!
                setSeekTarget(playbackController.getTime() + bufferLevel);
            }
        }
    }

    function startScheduleTimer(value) {
        clearTimeout(scheduleTimeout);

        scheduleTimeout = setTimeout(schedule, value);
    }

    function setFragmentProcessState (state) {
        if (isFragmentProcessingInProgress !== state ) {
            isFragmentProcessingInProgress = state;
        } else {
            logger.debug('isFragmentProcessingInProgress is already equal to', state);
        }
    }

    function processInitRequest(request) {
        if (request) {
            setFragmentProcessState(true);
            fragmentModel.executeRequest(request);
        }
    }

    function processMediaRequest(request) {
        if (request) {
            logger.debug('Next fragment request url is ' + request.url);
            fragmentModel.executeRequest(request);
        } else { // Use case - Playing at the bleeding live edge and frag is not available yet. Cycle back around.
            if (playbackController.getIsDynamic()) {
                logger.debug('Next fragment seems to be at the bleeding live edge and is not available yet. Rescheduling.');
            }
            setFragmentProcessState(false);
            startScheduleTimer(settings.get().streaming.lowLatencyEnabled ? 100 : 500);
        }
    }

    function switchTrackAsked() {
        switchTrack = true;
    }

    function replaceRequest(request) {
        replaceRequestArray.push(request);
    }

    function completeQualityChange(trigger) {
        if (playbackController && fragmentModel) {
            const item = fragmentModel.getRequests({
                state: FragmentModel.FRAGMENT_MODEL_EXECUTED,
                time: playbackController.getTime(),
                threshold: 0
            })[0];
            if (item && playbackController.getTime() >= item.startTime) {
                if ((!lastFragmentRequest.mediaInfo || (item.mediaInfo.type === lastFragmentRequest.mediaInfo.type && item.mediaInfo.id !== lastFragmentRequest.mediaInfo.id)) && trigger) {
                    eventBus.trigger(Events.TRACK_CHANGE_RENDERED, {
                        mediaType: type,
                        oldMediaInfo: lastFragmentRequest.mediaInfo,
                        newMediaInfo: item.mediaInfo
                    });
                }
                if ((item.quality !== lastFragmentRequest.quality || item.adaptationIndex !== lastFragmentRequest.adaptationIndex) && trigger) {
                    eventBus.trigger(Events.QUALITY_CHANGE_RENDERED, {
                        mediaType: type,
                        oldQuality: lastFragmentRequest.quality,
                        newQuality: item.quality
                    });
                }
                lastFragmentRequest = {
                    mediaInfo: item.mediaInfo,
                    quality: item.quality,
                    adaptationIndex: item.adaptationIndex
                };
            }
        }
    }

    function onStreamCompleted(e) {
        if (e.request.mediaInfo.streamInfo.id !== streamId || e.request.mediaType !== type) return;

        stop();
        setFragmentProcessState(false);
        logger.info(`Stream ${streamId} is complete`);
    }


    function downloadFinishNotification(playerId, chunkId){

        var quality = -2;
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://localhost:8333", false);
        xhr.onreadystatechange = function() {
            if ( xhr.readyState == 4 && xhr.status == 200 ) {
                quality = parseInt(xhr.responseText, 10);

            }
        }

        // need current header
        // need request url
        
        var data = {
            'run_schedule': 1,
            'playerId': playerId,
            'chunkId': chunkId
        };
        xhr.send(JSON.stringify(data));

    }
    // The chunk (Fragment) download finish
    function onFragmentLoadingCompleted(e) {
        if (e.request.mediaInfo.streamInfo.id !== streamId || e.request.mediaType !== type) return;

        logger.info('OnFragmentLoadingCompleted - Url:', e.request ? e.request.url : 'undefined', e.request.range ? ', Range:' + e.request.range : '');
        
        // console.log("type: " + e.request.mediaType);
        if (e.request.mediaType == "video" && e.request.type != "InitializationSegment"){ 
            console.log("Player Id: " + abrController.getPlayerId());
            console.log("Chunk Id: " + e.request.index);

            // send the download finish notification here
            downloadFinishNotification(abrController.getPlayerId(), e.request.index);
        }
        
        if (adapter.getIsTextTrack(mimeType)) {
            setFragmentProcessState(false);
        }

        if (e.error && e.request.serviceLocation && !isStopped) {
            replaceRequest(e.request);
            // console.log("replaceRequest - onFragmentLoadingCompleted")
            setFragmentProcessState(false);
            startScheduleTimer(0);
        }

        if (replacingBuffer) {
            mediaRequest = e.request;
        }
    }

    function onPlaybackTimeUpdated() {
        completeQualityChange(true);
    }

    function onBytesAppended(e) {
        if (e.streamId !== streamId || e.mediaType !== type) return;

        if (replacingBuffer && !isNaN(e.startTime)) {
            replacingBuffer = false;
            fragmentModel.addExecutedRequest(mediaRequest);
        }

        setFragmentProcessState(false);
        if (isReplacementRequest && !isNaN(e.startTime)) {
            //replace requests process is in progress, call schedule in n seconds.
            //it is done in order to not add a fragment at the new quality at the end of the buffer before replace process is over.
            //Indeed, if schedule is called too early, the executed request tested is the same that the one tested during previous schedule (at the new quality).
            const currentTime = playbackController.getTime();
            const fragEndTime = e.startTime + currentRepresentationInfo.fragmentDuration;
            const safeBufferLevel = currentRepresentationInfo.fragmentDuration * 1.5;
            if ((currentTime + safeBufferLevel) >= fragEndTime) {
                startScheduleTimer(0);
            } else {
                startScheduleTimer((fragEndTime - (currentTime + safeBufferLevel)) * 1000);
            }
            isReplacementRequest = false;
        } else {
            startScheduleTimer(0);
        }
    }

    function onFragmentLoadingAbandoned(e) {
        if (e.streamId !== streamId || e.mediaType !== type) return;

        logger.info('onFragmentLoadingAbandoned request: ' + e.request.url + ' has been aborted');
        if (!playbackController.isSeeking() && !switchTrack) {
            logger.info('onFragmentLoadingAbandoned request: ' + e.request.url + ' has to be downloaded again, origin is not seeking process or switch track call');
            replaceRequest(e.request);
            // console.log("replaceRequest - onFragmentLoadingAbandoned")

        }
        setFragmentProcessState(false);
        startScheduleTimer(0);
    }

    function onDataUpdateStarted(e) {
        if (e.sender.getType() !== type || e.sender.getStreamId() !== streamId) return;
        // stop();
    }

    function onBufferingCompleted(e) {
        if (type !== e.mediaType || streamId !== e.streamId) return;
        stop();
    }

    function onBufferCleared(e) {
        if (e.streamId !== streamId || e.mediaType !== type) return;

        if (replacingBuffer && settings.get().streaming.flushBufferAtTrackSwitch) {
            // For some devices (like chromecast) it is necessary to seek the video element to reset the internal decoding buffer,
            // otherwise audio track switch will be effective only once after previous buffered track is consumed
            playbackController.seek(playbackController.getTime() + 0.001, false, true);
        }

        // (Re)start schedule once buffer has been pruned after a QuotaExceededError
        if (e.hasEnoughSpaceToAppend && e.quotaExceeded) {
            start();
        }
    }

    function onQuotaExceeded(e) {
        if (e.streamId !== streamId || e.mediaType !== type) return;

        // Stop scheduler (will be restarted once buffer is pruned)
        stop();
        setFragmentProcessState(false);
    }

    function onURLResolutionFailed() {
        fragmentModel.abortRequests();
        stop();
    }

    function onInitQuota(e) {
        bufferQuota = e.quota;
    }

    function onPlaybackStarted() {
        if (isStopped || !settings.get().streaming.scheduleWhilePaused) {
            start();
        }
    }

    function onPlaybackSeeking(e) {
        setSeekTarget(e.seekTime);
        setTimeToLoadDelay(0);

        if (isStopped) {
            start();
        }

        const latency = currentRepresentationInfo.DVRWindow && playbackController ? currentRepresentationInfo.DVRWindow.end - playbackController.getTime() : NaN;
        dashMetrics.updateManifestUpdateInfo({
            latency: latency
        });

        if (!isFragmentProcessingInProgress) {
            // No pending request, request next segment at seek target
            startScheduleTimer(0);
        } else {
            // Abort current request
            fragmentModel.abortRequests();
        }
    }

    function onPlaybackRateChanged(e) {
        dashMetrics.updatePlayListTraceMetrics({playbackspeed: e.playbackRate.toString()});
    }

    function setSeekTarget(value) {
        seekTarget = value;
    }

    function setTimeToLoadDelay(value) {
        timeToLoadDelay = value;
    }

    function getTimeToLoadDelay() {
        return timeToLoadDelay;
    }

    function getBufferTarget() {
        return bufferLevelRule.getBufferTarget(type, currentRepresentationInfo);
    }

    function getType() {
        return type;
    }

    function getStreamId() {
        return streamId;
    }

    function resetInitialSettings() {
        checkPlaybackQuality = true;
        isFragmentProcessingInProgress = false;
        timeToLoadDelay = 0;
        seekTarget = NaN;
        initialRequest = true;
        lastInitQuality = NaN;
        lastFragmentRequest = {
            mediaInfo: undefined,
            quality: NaN,
            adaptationIndex: NaN
        };
        topQualityIndex = {};
        replaceRequestArray = [];
        isStopped = true;
        switchTrack = false;
        replacingBuffer = false;
        mediaRequest = null;
        isReplacementRequest = false;
    }

    function reset() {
        //eventBus.off(Events.LIVE_EDGE_SEARCH_COMPLETED, onLiveEdgeSearchCompleted, this);
        eventBus.off(Events.DATA_UPDATE_STARTED, onDataUpdateStarted, this);
        eventBus.off(Events.FRAGMENT_LOADING_COMPLETED, onFragmentLoadingCompleted, this);
        eventBus.off(Events.STREAM_COMPLETED, onStreamCompleted, this);
        eventBus.off(Events.BUFFER_CLEARED, onBufferCleared, this);
        eventBus.off(Events.BYTES_APPENDED_END_FRAGMENT, onBytesAppended, this);
        eventBus.off(Events.QUOTA_EXCEEDED, onQuotaExceeded, this);
        eventBus.off(Events.PLAYBACK_SEEKING, onPlaybackSeeking, this);
        eventBus.off(Events.PLAYBACK_STARTED, onPlaybackStarted, this);
        eventBus.off(Events.PLAYBACK_RATE_CHANGED, onPlaybackRateChanged, this);
        eventBus.off(Events.PLAYBACK_TIME_UPDATED, onPlaybackTimeUpdated, this);
        eventBus.off(Events.URL_RESOLUTION_FAILED, onURLResolutionFailed, this);
        eventBus.off(Events.FRAGMENT_LOADING_ABANDONED, onFragmentLoadingAbandoned, this);
        eventBus.off(Events.BUFFERING_COMPLETED, onBufferingCompleted, this);
        eventBus.off(Events.INITQUOTA, onInitQuota, this);

        stop();
        completeQualityChange(false);
        resetInitialSettings();
    }

    instance = {
        initialize: initialize,
        getType: getType,
        getStreamId: getStreamId,
        setCurrentRepresentation: setCurrentRepresentation,
        setSeekTarget: setSeekTarget,
        setTimeToLoadDelay: setTimeToLoadDelay,
        getTimeToLoadDelay: getTimeToLoadDelay,
        switchTrackAsked: switchTrackAsked,
        isStarted: isStarted,
        start: start,
        stop: stop,
        reset: reset,
        getBufferTarget: getBufferTarget,
        processInitRequest: processInitRequest,
        processMediaRequest: processMediaRequest
    };

    setup();

    return instance;
}

ScheduleController.__dashjs_factory_name = 'ScheduleController';
export default FactoryMaker.getClassFactory(ScheduleController);
