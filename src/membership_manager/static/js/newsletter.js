
function manageNewsletter(url){
    obj = {
        url: url,
        loadEmails: ()=>{
             $.ajax({
              dataType: "json",
              url: url,
              type: "POST",
              headers: {'X-CSRFToken': getCookie('csrftoken') },
              data: {'recipient': $(".datafilter").find(':input').serialize()},
              success: function(data){
                    for (var x=0; x<data['emails'].length; x++){
                         $('input[name="recipient"]').data('tagify').addTags(data['emails'][x])
                    }
              }
              });
        },
        clearEmails: ()=>{
            $('input[name="recipient"]').data('tagify').removeAllTags();
        },
        showPreview: ()=>{
            console.log("BINGO")
        },
        tabrouter: function(e){
            if(e.target.id == 'tabpreview'){
                this.showPreview();
            }
        },
        initialize: function(){
            $('a[data-toggle="tab"]').on('shown.bs.tab',  this.tabrouter );
            $("#loadremitentes").on('click', this.loadEmails());
            $("#clearremitentes").on('click', this.clearEmails());
        }


    }

    obj.initialize();
    return obj;
}