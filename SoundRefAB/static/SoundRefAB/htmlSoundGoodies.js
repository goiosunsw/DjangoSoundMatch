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


var waitDlg;
waitDlg = waitDlg || (function () {
    var pleaseWaitDiv = 
        $('<div class="modal fade" id="pleaseWaitDialog"  role="dialog"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h1>Loading...</h1></div><div class="modal-body"><div class="progress progress-striped active"><div class="progress-bar"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div></div></div></div></div></div>');
    return {
        showPleaseWait: function() {
            pleaseWaitDiv.modal('show');
        },
        hidePleaseWait: function () {
            pleaseWaitDiv.modal('hide');
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
    $(audioEl).data('played',true);
    allAudio = $('audio');
    var allPlayed = true;
    but = $(audioEl).siblings('input[type=button]');
    but.removeClass('btn-warning').addClass('btn-default');
    
    for(i=0;i<allAudio.length;i++) {
        if (!allAudio.eq(i).data('played')){
            allPlayed = false;
        }
    }
    if (allPlayed) {
        $('#submit').removeClass('disabled');
    }
};

newAudioLoaded = function(audioEl) {
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

validateAudio = function(theForm) {
    if ($('#submit').hasClass('disabled')){
        alertModal('Please listen to all sounds before continuing').showAlert();
        $('audio').each(function(){
            but = $(this).siblings('input[type=button]')
            if (!$(this).data('played')){
                but.removeClass('btn-default').addClass('btn-warning');
            }
        });
        return false;
    } 
    else { 
        return true;
    }
};


$(document).ready(function() {
    $(document).data('showndate',(new Date()).valueOf());
    waitDlg.showPleaseWait();
    sounds = $('audio');
    sounds.data('played',false);
    
    sounds.each(function(i,e){
        $(e).on('canplaythrough', function(){newAudioLoaded(e);});
        thisButton = $(e).siblings('input[type=button]');
        thisButton.attr('onclick','');
        thisButton.on('click',function(){playAndDoStuff(e)});
    });
});

