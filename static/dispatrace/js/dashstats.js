
$(document).ready(function () {
    
    $.ajax({
        method: "GET",
        url: $('#statsurl').attr('dash-stats-url'),
        data: {},
        success: function (res,) {
            $('#intrayCount').html(res.intray_count);
            $('#outtrayCount').html(res.outtray_count);
            $('#closedCount').html(res.closed_count);
            $('#archivedCount').html(res.archived_count);
            $('#draftsCount').html(res.drafts_count);
        },
        error: function () { },
    });

});