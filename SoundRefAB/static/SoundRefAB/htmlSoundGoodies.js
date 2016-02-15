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


playAndDoStuff = function(audioEl) {
    console.log(audioEl);
    audioEl.play();
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
        alert('Please listen to all sounds before continuing');
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

