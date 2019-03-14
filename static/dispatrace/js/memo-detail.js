
$(document).ready(function () {

    // Reveal Add Comment Form
    $('.revealComment').on('click', function (e) {
        $('.memoCommentForm').slideToggle('slow');
    });

    // Reveal Add Recipients Form
    $('.revealAddRecipient').on('click', function (e) {
        $('.addRecipient').slideToggle('slow');
        //removeAttr("style");
    }); 

     // Reveal Add Fuel request Form
    $('.revealAddFuelRequest').on('click', function (e) {
        $('.addFuelRequest').slideToggle('slow');
    });

    // Reveal AddTo Form
    $('.revealTo').on('click', function (e) {
        $('#memoto').hide();
        $('.addTo').slideToggle('slow');
    });

    // CommentForm Submit with Ajax    
    $('#memoCommentFormm').on('submit', function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        
        var messages_area = $(this).siblings("div.messages");
        var $form = $(this);

        $.ajax({
            method: $(this).attr('method'),
            url: $(this).attr('action'),
            data: {
                comment: $(this).find("textarea#comment").val(),
                password_confirm: $(this).find("input#password_confirm").val(),
            },
            success: function (res) {
                if (res.pass_passed === 'yes') {
                    $form.hide();
                    messages_area.removeClass('bg-danger');
                    messages_area.addClass('bg-success');
                    messages_area.html('');
                    messages_area.html(res.success_message);
                    window.setTimeout(function () { window.location.reload() }, 1000);
                } else {
                    messages_area.html(res.success_message);
                    messages_area.addClass('bg-danger');
                }
            },
            error: function (res) {},
        });
    });

    // Submit Atach Fuel Form
    $("form#fuelRequestFormm").on('submit', function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        
        var messages_area = $(this).siblings("div.messages");
        var $form = $(this);

        $.ajax({
            method: "POST",
            url: $(this).attr('action'),
            data: {
                amount: $(this).find("input#amount").val(),
                priority: $(this).find("select#priority").val(),
                fuel_type: $(this).find("select#fuel_type").val(),
                c_password: $(this).find("input#password_confirm").val(),
            },
            success: function (res) {
                if (res.pass_passed === 'yes') {
                    $form.hide();
                    messages_area.removeClass('bg-danger');
                    messages_area.addClass('bg-success');
                    messages_area.html('');
                    messages_area.html(res.success_message);
                    window.setTimeout(function () { window.location.reload() }, 1000);
                } else {
                    messages_area.html(res.success_message); 
                    messages_area.addClass('bg-danger');
                }
            },
            error: function (res) {},
        });
    });

    // Submit AddTo Form
    $("form#addToForm").on('submit', function (e) {
        e.preventDefault();
        $.ajax({
            method: "POST",
            url: $(this).attr('action'),
            data: {
                to: $(this).find("input#to").val(),
            },
            success: function (res) {
                window.location.reload();
                $('form#addToForm')[0].reset();
            },
            error: function (res) {
                $('.usernotfound').slideToggle('slow');
            },
        });
    });

    // CloseMemo for Archiving
    $("button#memo-close").on('click', function (e) {
        e.preventDefault();
        var messages_area = $(this).siblings("div.messages");
        $.ajax({
            method: "POST",
            url: $(this).attr('close-url'),
            data: {
                close: 'True',
            },
            success: function (res) {
                $("button#memo-close").toggle('slow', function () {
                    // after hiding do the following
                    messages_area.html(res.close_message);
                    messages_area.addClass('bg-success');
                });
                $('#editComment').css('display', 'none');
                window.setTimeout(function () { window.location.reload() }, 1000);
            },
            error: function (res) {},
        });
    });

    // Reception Acknowledgement
    $("button#memo-acknowledge-reception").on('click', function (e) {
        e.preventDefault();
        var messages_area = $(this).siblings("div.messages");
        $.ajax({
            method: "POST",
            url: $(this).attr('recept-url'),
            data: {
                recept: 'True',
            },
            success: function (res) {
                $("button#memo-acknowledge-reception").toggle('slow', function () {
                    // after hiding do the following
                    messages_area.html(res.close_message);
                    messages_area.addClass('bg-success');
                });
                $('#editComment').css('display', 'none');
                window.setTimeout(function () { window.location.reload() }, 1000);
            },
            error: function (res) { },
        });
    });

    // Archiving Memos
    $("button#memo-archive").on('click', function (e) {
        e.preventDefault();
        var messages_area = $(this).siblings("div.messages");
        $.ajax({
            method: "POST",
            url: $(this).attr('archive-url'),
            data: {
                archive: 'True',
            },
            success: function (res) {
                $("button#memo-archive").toggle('slow', function () {
                    // after hiding do the following
                    messages_area.html(res.archive_message);
                    messages_area.addClass('bg-success');
                });
                window.setTimeout(function () { window.location.reload() }, 1000);
            },
            error: function (res) {},
        });
    });

    // Send Memo for approval or viewing
    $("form#SendForm").on('submit', function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        var $form = $(this);
        var messages_area = $(this).siblings("div.messages");
        $.ajax({
            method: "POST",
            url: $(this).attr('action'),
            data: {
                send: 'True',
                c_password: $(this).find("input#c_password").val(),
            },
            success: function (res) {
                if (res.pass_passed === 'yes') {
                    $form.hide();
                    messages_area.removeClass('bg-danger');
                    messages_area.addClass('bg-success');
                    messages_area.html('');
                    messages_area.html(res.success_message);
                    window.setTimeout(function () { window.location.reload() }, 1000);
                } else {
                    messages_area.html(res.success_message); 
                    messages_area.addClass('bg-danger');
                }
            },
            error: function (res) {},
        });
    });

    // Submit Add recipient Form
    $("form#addRecipientForm").on('submit', function (e) {
        e.preventDefault();
        var recipients = $("input#recipients").val();
        var url = $(this).attr('action');
        data = {
            recipients: recipients,
        }
        $.ajax({
            method: "POST",
            url: url,
            data: data,
            success: function () {
                window.location.reload();
                $('form#addRecipientForm')[0].reset();
            },
            error: function (res) {
                $('.usernotfound').slideToggle('slow');
            },
        });
    });
    

    // Comment Edit/Update: GET
    $("span.comment-href").on('click', function (e) {
        var getURL = $(this).attr('data-get-href');
        $.ajax({
            method: "GET",
            url: getURL,
            data: {},
            success: function (res, getURL) {
                console.log(res);
                $(res.form_id).slideToggle('slow');
                $(res.form_id.concat(" textarea")).html(res.comment);
            },
            error: function () { },
        });
    });

    // Comment Edit/Update: POST
    $("form").on('submit', function (e) {
        e.preventDefault();

        var $form = $(this);
        var postURL = $(this).attr('action');
        var comment_new = $(this).find('textarea#comment').val();
        var password_confirm = $(this).find('#password_confirm').val();
        var messages_area = $(this).siblings("div.messages");

        $.ajax({
            method: "POST",
            url: postURL,
            dataType: 'json',
            data:{
                comment: comment_new,
                password_confirm: password_confirm,
            },
            success: function (res) {
                if (res.pass_passed === 'yes') {
                    $form.hide();
                    messages_area.removeClass('bg-danger');
                    messages_area.addClass('bg-success');
                    messages_area.html('');
                    messages_area.html(res.success_message);
                    window.setTimeout(function () { window.location.reload() }, 1000);
                } else {
                    messages_area.html(res.success_message); 
                    messages_area.addClass('bg-danger');
                }
            },
            error: function () { },
        });

    });


    $('.attachment-item').hover( 
        function(){
            $(this).removeClass('btn-info');        
            $(this).addClass('btn-success');
            $('.attachment-name-message').text($(this).attr('attatchment-name'));
            $('.attachmemt-messages').slideToggle(1000);
        }, 
        function(){ 
            $(this).removeClass('btn-success');
            $(this).addClass('btn-info');       
            $('.attachmemt-messages').slideToggle('slow');
        }
    );







});

