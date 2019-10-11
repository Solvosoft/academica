(function($) {
 $(document).ready(function() {
    if(window.location.href.indexOf("/change/") !== -1){
        $(".membership_template").remove()
    }else{

        $( "#id_membership_template" ).on('change', function() {
            var id = $(this).val();
            var attrs = window.location.search;
            if(attrs === ""){
                attrs="?tid=" + id
            }else{
                attrs= attrs+"&tid=" + id
            }
            window.location.href = window.location.pathname+attrs
        });
    }
    });
})(grp.jQuery);