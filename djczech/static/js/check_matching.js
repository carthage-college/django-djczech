$(function() {

    // dragging and dropping <tr> elements is difficult for some reason.
    // drobinson found this work-around:
    // https://stackoverflow.com/a/3592057
    var c = {};
    var j = {};

    // ajax post URL
    var earl = "https://www.carthage.edu/staging/djczech/reconciliation/matching/ajax/";

    /* spinner */
    var opts = {
        lines: 13, // The number of lines to draw
        length: 20, // The length of each line
        width: 10, // The line thickness
        radius: 30, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 0, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#000', // #rgb or #rrggbb or array of colors
        speed: 1, // Rounds per second
        trail: 60, // Afterglow percentage
        shadow: false, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'search-results', // The CSS class to assign to spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '50px', // Top position relative to parent in px
        left: 'auto' // Left position relative to parent in px
    };
    var container = document.getElementById("PanelsContainer");
    var spinner = new Spinner(opts).spin(container);
    spinner.stop(container);

    /* somewhat generic function for ajax POST */
    function xajax(data, target, j,  message) {
        $.ajax({
            type: "POST",
            url: earl,
            data: data,
            dataType: "json",
            cache: false,
            beforeSend: function(){
                spinner.spin(container);
            },
            success: function(data) {
                if (data) {
                    $(j.tr).remove();
                    $(j.helper).remove();
                    $(target).remove();
                    $('body').css('cursor', 'auto');
                    spinner.stop(container);
                    $.blockUI({
                        theme: true,
                        title: 'Success',
                        message:  '<p>' + message + '</p>',
                    });
                    $('.blockOverlay').click($.unblockUI);
                } else {
                    $('.blockOverlay').attr('title','Something went wrong:' + message).click($.unblockUI);
                    $.growlUI('Something went wrong','No match was made');
                }
            }
        });
    }

    // Create sortable table for Carthage Checks
    $("#CarthageChecks table").stupidtable();
    // attach drag and drop handlers
    $( "#CarthageChecks tbody tr ").draggable({
        helper: "clone",
        cursor: "move",
        revert: "true",
        containment: '#content',
        stack: '#CarthageChecks table',
        start: function(event, ui) {
            c.tr = this;
            c.helper = ui.helper;
        }
    });

    $( "#CarthageChecks tbody tr ").droppable({
        accept: '#JohnsonChecks tr',
        hoverClass: 'hovered',
        drop: function(event, ui) {
            var target = this;
            var CarthageNumber = $(this).children('td').eq(0).text();
            var CarthageAmount = $(this).children('td').eq(1).text();
            var JohnsonNumber = ui.draggable.children('td').eq(0).text();
            var JohnsonAmount = ui.draggable.children('td').eq(1).text();
            var JohnsonSequence = ui.draggable.attr('id')

            var data = {
                JohnsonSequence: JohnsonSequence,
                JohnsonNumber: JohnsonNumber,
                JohnsonAmount: JohnsonAmount,
                CarthageNumber: CarthageNumber,
                CarthageAmount: CarthageAmount
            }

            var message = "match Johnson (" + JohnsonSequence + ") "
                        + JohnsonNumber + "\t" + JohnsonAmount
                        + "\n         with Carthage " + CarthageNumber
                        + "\t" + CarthageAmount;

            // testing only
            console.log(message);
            // execute the ajax post
            xajax(data, target, j,  message);
        }
    });

    // Create sortable table for Johnson Bank Checks
    $("#JohnsonChecks table").stupidtable();

    // attach drag and drop handlers
    $("#JohnsonChecks tbody tr ").draggable({
        helper: "clone",
        cursor: "move",
        revert: "true",
        containment: '#content',
        stack: '#JohnsonChecks table',
        start: function(event, ui) {
            j.tr = this;
            j.helper = ui.helper;
        }
    });

    $("#JohnsonChecks tbody tr ").droppable({
        accept: '#CarthageChecks tr',
        hoverClass: 'hovered',
        drop: function(event, ui) {
            var target = this;
            var JohnsonNumber = $(this).children('td').eq(0).text();
            var JohnsonAmount = $(this).children('td').eq(1).text();
            var JohnsonSequence = $(this).attr('id');
            var CarthageNumber = ui.draggable.children('td').eq(0).text();
            var CarthageAmount = ui.draggable.children('td').eq(1).text();

            var data = {
                JohnsonSequence: JohnsonSequence,
                JohnsonNumber: JohnsonNumber,
                JohnsonAmount: JohnsonAmount,
                CarthageNumber: CarthageNumber,
                CarthageAmount: CarthageAmount
            }

            var message = "match Carthage " + CarthageNumber + "\t"
                        + CarthageAmount + "\n          with Johnson "
                        + JohnsonNumber + "\t" + JohnsonAmount;

            // testing only
            console.log(message);
            // execute the ajax post
            xajax(data, target, j,  message);
        }
    });
});
