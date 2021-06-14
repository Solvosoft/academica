function myFunction(id) {
    let x = document.getElementById(id)
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
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
            result = data['result'];
            if (result == "" ){
                result = "Error al cargar los datos";
            }
            $('#result_modal').html(result);
            if (result != ""){
                $('#id_country').select2({});
                $("#id_password").after("<input type='checkbox' onclick='myFunction(\"id_password\")'> Mostrar contraseña<br/>");
                $("#id_password2").after("<input type='checkbox' onclick='myFunction(\"id_password2\")'> Mostrar contraseña<br/>");
                $('#show_password').parent().css({'text-align':'left', "margin-bottom":"5px"});
                $('#pills-tab li:nth-child('+data['display_form']+') a').tab('show');
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
            if(data['show_modal'] == "on"){
                $('#showModal').modal('show');
                if (data['login_errors']){
                    $("#login-errors").show()
                }
            }
            if(data['student_created'] == 'on'){
                Toast.fire({
                    icon: 'success',
                    title: 'El usuario fue creado exitosamente, deberá acceder a su correo para validar su cuenta e iniciar sesión.'
                });
            }
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
                            console.log(rows.text)
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
        },error: function(xhr, ajaxOptions, thrownError){
            if(xhr.status==404) {
                $('#result_modal').html("Error al cargar los datos");
            }
        }
    });
});