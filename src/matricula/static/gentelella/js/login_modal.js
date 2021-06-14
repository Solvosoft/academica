function myFunction(id) {
    let x = document.getElementById(id)
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}
function tagify(){
    var input = document.querySelector('#id_organization'),
    tagify = new Tagify(input, {whitelist:[]}),
    controller; // for aborting the call
    // listen to any keystrokes which modify tagify's input
    tagify.on('input', onInput)
    function onInput( e ){
        var value = e.detail.value;
        tagify.settings.whitelist.length = 0; // reset the whitelist

        // https://developer.mozilla.org/en-US/docs/Web/API/AbortController/abort
        controller && controller.abort();
        controller = new AbortController();

        // show loading animation and hide the suggestions dropdown
        tagify.loading(true).dropdown.hide.call(tagify)

        fetch("/gtapis/student/?q="+e.detail.value, {signal:controller.signal})
        .then(RES => RES.json())
        .then(function(whitelist){
            // update inwhitelist Array in-place
            var whitelst = []
            for(rows of whitelist.results){
                if(rows.text != ""){
                    tags = JSON.parse(rows.text)
                    for(tag of tags){
                        whitelst.push(tag.value)
                    }
                }
            }
            tagify.settings.whitelist.splice(0, whitelist.total_count, ...whitelst)
            tagify.loading(false).dropdown.show.call(tagify, value); // render the suggestions dropdown
        })
    }
}
$('#showModal').on('show.bs.modal', function (e) {
    let modal = 1;
    if(e.relatedTarget.id == "enroll"){
        modal = 2;
    }
    $.ajax({
        url: modal_context.forms_url+'?modal='+modal,
        method: 'GET',
        dataType: "json",
        success: function(data){
            result = JSON.parse(data['content']);
            if (result == "" ){
                result = "Error al cargar los datos";
            }
            $('#result_modal').html(result['result']);
            if (result != ""){
                $('#id_country').select2({});
                $("#id_password").after("<input type='checkbox' onclick='myFunction(\"id_password\")'> Mostrar contraseña<br/>");
                $("#id_password2").after("<input type='checkbox' onclick='myFunction(\"id_password2\")'> Mostrar contraseña<br/>");
                $('#show_password').parent().css({'text-align':'left', "margin-bottom":"5px"});
                $('#pills-tab li:nth-child('+result['display_form']+') a').tab('show');
                if(data['display_form'] == '2'){
                    $('#title').html("Registrarme");
                }else{
                    $('#title').html("Iniciar Sesión");
                }
                $('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
                    $('#title').html($(this).html());
                });
                $('.select2-container').css('width','100%');
            }
            tagify()
        },error: function(xhr, ajaxOptions, thrownError){
            if(xhr.status==404) {
                $('#result_modal').html("Error al cargar los datos");
            }
        }
    });
    function doLogin(modal){
        login = {
            "modal": modal,
            "username": $("#id_username").val(),
            "password2": $("#id_password2").val(),
        };

        $.ajax({
            url: modal_context.url_login+"?modal="+modal,
            method: "POST",
            dataType: "json",
            data: login,
            headers: {'X-CSRFToken': getCookie('csrftoken') },
            success: function(data){
                result = JSON.parse(data['content']);
                if(result['result']=='error'){
                    Toast.fire({
                        icon: 'error',
                        title: modal_context.validation_error,
                    });
                    $('#result_modal').html(result['data']);
                    $('#pills-tab li:nth-child('+result['display_form']+') a').tab('show');
                    $("#id_password2").after("<input type='checkbox' onclick='myFunction(\"id_password2\")'> Mostrar contraseña<br/>");
                    tagify();
                    $('#id_country').select2({});
                }else if(result['result'] == 'ok'){
                    $('#showModal').modal('hide');
                    Swal.fire({
                        title:'Inicio de sesión exitosa',
                        icon:'success',
                        timer: 1500,
                    }).then((result) => {
                       location.reload(); 
                    });
                }else{
                    $('#result_modal').html(result['data']);
                    tagify();
                    $('#id_country').select2({});
                    $('#pills-tab li:nth-child('+result['display_form']+') a').tab('show');
                    $("#id_password2").after("<input type='checkbox' onclick='myFunction(\"id_password2\")'> Mostrar contraseña<br/>");
                    Toast.fire({
                        icon: 'error',
                        title: modal_context.non_validation_error,
                    });
                }
            },
            error: function(xhr, ajaxOptions, thrownError){
                Toast.fire({
                    icon: 'error',
                    title: "Ocurrio un error mientras se realizaba la operación.",
                });
            }
        });
    }

    function enrollUser(modal){
        enroll = {
            "modal": modal,
            "name": $("#id_name").val(),
            "first_name": $("#id_first_name").val(),
            "last_name": $("#id_last_name").val(),
            "email": $("#id_email").val(),
            'phone_number': $("#id_phone_number").val(),
            'country': $('#id_country').val(),
            "password": $("#id_password").val(),
            "organization": $("#organization").val(),
        };
        $.ajax({
            url: modal_context.url_enroll+"?modal="+modal,
            method: "POST",
            dataType: "json",
            data: enroll,
            headers: {'X-CSRFToken': getCookie('csrftoken') },
            success: function(data){
                result = JSON.parse(data['content']);
                if(result['result']=='error'){
                    Toast.fire({
                        icon: 'error',
                        title: modal_context.validation_error,
                    });
                    $('#result_modal').html(result['data']);
                    $('#pills-tab li:nth-child('+result['display_form']+') a').tab('show');
                    tagify();
                    $("#id_password").after("<input type='checkbox' onclick='myFunction(\"id_password\")'> Mostrar contraseña<br/>");
                    $('#id_country').select2({});
                }else if(result['result'] == 'ok'){
                    Swal.fire({
                        title:'El usuario ha sido creado con éxito!',
                        icon:'success',
                        timer: 1500,
                    });
                }else{
                    Toast.fire({
                        icon: 'error',
                        title: modal_context.non_validation_error,
                    });
                }
            },
            error: function(xhr, ajaxOptions, thrownError){
                Toast.fire({
                    icon: 'error',
                    title: "Ocurrio un error mientras se realizaba la operación.",
                });
            }
        });
    }
    $(document).on('click', '#btn_login, #btn_enroll', function(e){
        modal = e.target.value
        if(modal == "1"){
            doLogin(modal);
        }else{
            enrollUser(modal);
        }
        return false;
    });
});