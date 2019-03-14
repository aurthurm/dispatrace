
    $(document).ready(function(){// Enable Django CSRF-ready AJAX Calls

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        var csrftoken = getCookie('csrftoken');

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        // toggling pedamuse search fucntion on
        $('span#search-toggler').click(function(){
            $('#pedamuseSearch').slideToggle('slow');
        });

        //enable tooltips
        $(function () {
          $('[data-toggle="tooltip"]').tooltip()
        })
        $('.ui-icon.ui-icon-trash').html('<i class="fa fa-trash"></i>');
        $('.ui-icon.ui-icon-trash').addClass("btn btn-sm btn-danger");

        $('input').on('focusout', function(){
            $('.ui-icon.ui-icon-trash').html('<i class="fa fa-trash"></i>');
            $('.ui-icon.ui-icon-trash').addClass("btn btn-sm btn-danger");
        });

        // prevent notifications from closin when clickes
        $('#notificationDrop.dropdown-menu').on('click', function(e) {
          e.stopPropagation();
        });

        // update notificatio counts
        function get_not_counts(){
            $.ajax({
                method: 'GET',
                url: '/notification-count',
                data: {},
                success: function(res){
                    $('#unreadNot').html(res.unread);
                    $('#allNot').html(res.active);
                }
            })            
        }
        if ($('#getNotification').val() === "true"){
            get_not_counts();
            setInterval(function(){get_not_counts()},5000);
        }


    })