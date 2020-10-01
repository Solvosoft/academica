(function($){

    $('#id_report_type').on('select2:select', function (e) {

        var tipo_reporte = e.params.data['id'];
        var url = "/reports/"+tipo_reporte+"/";

        $.ajax({
                url: url,
                type : "GET",
                dataType : 'json',
                success : function(result) {


                    if(result['filters']){

                        $('#filters_extra').html(result['message']);
                        $('#reporte').addClass('col-sm-8').removeClass('col-sm-12');
                        $('#content_filters_extra').show();

                     if(result.hasOwnProperty('script')){
                        eval(result['script'])
                    }

                    }else{
                        $('#reporte').addClass('col-sm-12').removeClass('col-sm-8');
                        $('#content_filters_extra').hide();
                    }

                },
                error: function(xhr, resp, text) {
                    console.log(xhr, resp, text);
                }

        });

    });


})(jQuery);