/* 
 * htmlSoundGoodies.js - 
 * Part of DjangoSoundMatch psychoacoustics package
 * Utilities to check:
 * - sounds have been downloaded
 * - sounds have been played
 * - questions have been answered
 *
 *
 */


var timeOutDialog;
timeOutDialog = timeOutDialog|| (function () {
    var timeOutDiv = 
        $('<div class="modal fade" id="timeOutDialog"  role="dialog"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h1>Warning</h1></div><div class="modal-body"><p>Audio is taking too long to download.</p><p>You may need to press "Play" sveral times before you can hear a continuous tone.</p></div></div></div></div>');
    
    return {
        showTimeOut: function() {
            waitDlg.hidePleaseWait();
            timeOutDiv.modal('show');
        },
        hideTimeOut: function () {
            timeOutDiv.modal('hide');
        },

    };
})();


var waitDlg;
waitDlg = waitDlg || (function () {
    var pleaseWaitDiv = 
        $('<div class="modal fade" id="pleaseWaitDialog"  role="dialog"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h1>Loading...</h1></div><div class="modal-body"><div class="progress progress-striped active"><div class="progress-bar"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div></div></div></div></div></div>');
    var timeOutObj;
    
    return {
        showPleaseWait: function() {
            $.fn.modal.prototype.constructor.Constructor.DEFAULTS.backdrop = 'static';
            pleaseWaitDiv.modal('show');
            pleaseWaitDiv.modal({
                backdrop: 'static',
                keyboard: false
            });
            this.timeOutObj = setTimeout(function(){
                waitDlg.hidePleaseWait();
                alertModal('Audio is taking too long to download. You may need to click Play several times before hearing the continuous tone.').showAlert();
            },20000);
        },
        hidePleaseWait: function () {
            pleaseWaitDiv.modal('hide');
            clearTimeout(this.timeOutObj);
            $.fn.modal.prototype.constructor.Constructor.DEFAULTS.backdrop = true;
        },

    };
})();

var alertModal;
alertModal = alertModal || (function (alertTxt) { 
    var alertDiv = 
        $('<div id="myModal" class="modal" role="dialog"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal">&times;</button><h4 class="modal-title">Warning</h4></div><div class="modal-body"><p>'+alertTxt+'</p></div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal">Close</button></div></div></div></div>');
    return {
        showAlert: function() {
            alertDiv.modal('show');
        },
        hideAlert: function () {
            alertDiv.modal('hide');
        },
        
    };
});
    
timestamp = function(label) {
    var showndate = $(document).data('showndate');
    var datedelay = Math.floor(((new Date().valueOf())-showndate)/1000);
    seqEl =  $('#playseq');
    if (seqEl) {
        orig = seqEl.attr('value');
        seqEl.attr('value',orig+label+":"+datedelay+";");
    }
}


playAndDoStuff = function(audioEl) {
    console.log(audioEl);
    audioEl.play();
    timestamp($(audioEl).attr('id').match(/\d+/));
    $(audioEl).data('valid',true);
    allAudio = $('audio');
    var allPlayed = true;
    but = $(audioEl).siblings('input[type=button]');
    but.removeClass('btn-warning').addClass('btn-default');
    
    for(i=0;i<allAudio.length;i++) {
        if (!allAudio.eq(i).data('valid')){
            allPlayed = false;
        }
    }
    if (allPlayed) {
        validatePage();
    }
};

newAudioLoaded = function(audioEl) {
    console.log(audioEl.id+' loaded' )
    $(audioEl).data('loaded',true);
    allAudio = $('audio');
    var allPlayed = true;
    for(i=0;i<allAudio.length;i++) {
        if (!allAudio.eq(i).data('loaded')){
            allPlayed = false;
        }
    }
    if (allPlayed) {
        waitDlg.hidePleaseWait();
    }
    
};

invalidAudioFunction = function() {
    alertModal('Please listen to all sounds before continuing').showAlert();
    $('audio').each(function(){
        but = $(this).siblings('input[type=button]')
        if (!$(this).data('valid')){
            but.removeClass('btn-default').addClass('btn-warning');
        }
    });
    
}



validatePage = function() {
    var reqItems;
    var valid = true;
    reqItems = $('*').filter(function() {
        return $(this).data('valid') !== undefined;
    });
    for (var i=0; i<reqItems.length; i++){
        if (!$(reqItems[i]).data('valid')){
            
            return false;
        }
    }
    // validation actions
    window.onbeforeunload = undefined;
    $('#submit').removeClass('disabled');
    return true;    
}

validateFormOnSubmit = function() {
    var reqItems;
    reqItems = $('*').filter(function() {
        return $(this).data('valid') !== undefined;
    });
    for (var i=0; i<reqItems.length; i++){
        if (!$(reqItems[i]).data('valid')){
            if ($(reqItems[i]).data('invalidAlert') !== undefined){
                $(reqItems[i]).data('invalidAlert')();
            }
            else {
                alertModal('Please check that all required questions have been answered and you listened to all sounds').showAlert();
            }
            return false;
        }
    }
    return true;
    
}

$(document).ready(function() {
    $(document).data('showndate',(new Date()).valueOf());
    window.onbeforeunload = function() { return "Your work will be lost."; };
    
    waitDlg.showPleaseWait();
    var sounds = $('audio');
    console.log('Document.ready');
    sounds.data('valid',false);
    sounds.data('loaded',false);
    sounds.data('invalidAlert',invalidAudioFunction)
    sounds.each(function(i,e){
        //$(e).on('canplaythrough', function(){newAudioLoaded(e);});
        $(e).on('canplaythrough', function(){newAudioLoaded(e);});
        thisButton = $(e).siblings('input[type=button]');
        thisButton.attr('onclick','');
        thisButton.on('click',function(){playAndDoStuff(e)});
        console.log('Setting up audio obj '+i);
        $(e).on('stalled', function() { 
            var audio = this;
            audio.load();
            console.log('Reloading '+this.id);

            audio.play();
            audio.pause();
        });
    });
    var allLoaded = true;
    // remove wait dialog if all sounds are loaded by this time
    // because oncanplaythrough will never be called
    for(i=0;i<sounds.length;i++) {
        if (sounds[i].readyState<4 && sounds[i].src.length>0){
            allLoaded = false;
        }
    }
    if (allLoaded) {
        waitDlg.hidePleaseWait();
    }
    
});

