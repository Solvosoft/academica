
function manageNewsletter(url, previewurl){
    obj = {
        url: url,
        previewurl: previewurl,
        loadEmails: function(){
             $.ajax({
              dataType: "json",
              url: url,
              type: "POST",
              headers: {'X-CSRFToken': getCookie('csrftoken') },
              data: {'recipient': $(".datafilter").find(':input').serialize()},
              success: function(data){
                    for (var x=0; x<data['emails'].length; x++){
                         $('input[name="recipient"]').data('tagify').removeAllTags();
                         $('input[name="recipient"]').data('tagify').addTags(data['emails'][x])
                    }
              }
              });
        },
        clearEmails: function(){
            $('input[name="recipient"]').data('tagify').removeAllTags();
        },
        showPreview: function(){
             $.ajax({
              dataType: "html",
              url: previewurl,
              type: "POST",
              headers: {'X-CSRFToken': getCookie('csrftoken') },
              data: {'data': $('#id_message').val()},
              success: function(data){
                     $("#preview iframe").contents().find("body").html(data);

              }
              });
        },
        tabrouter: function(e, parent){
            if(e.target.id == 'tabpreview'){
                parent.showPreview();
            }
        },
        saveform: function(){
            $('input[name="filters"]').val($("#formfilters").serialize());
            $('#formcreatenewsletter').submit();
        },
        initialize: function(){
            $('a[data-toggle="tab"]').on('shown.bs.tab', (e)=>( this.tabrouter(e, this)));
            $("#loadremitentes").on('click', this.loadEmails);
            $("#clearremitentes").on('click', this.clearEmails);
            $("#createnewsletter").on('click', this.saveform);
        }
    }

    obj.initialize();
    return obj;
}