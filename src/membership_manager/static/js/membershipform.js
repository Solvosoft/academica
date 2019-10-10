(function($) {
 $(document).ready(function() {
    if(window.location.href.indexOf("/change/") !== -1){
        $(".membership_template").remove()
    }else{
        $( "#id_membership_template" ).on('change', function() {
            var id = $(this).val();
            window.location.href = window.location.href+"?tid=" + id
        });
    }
    });
})(grp.jQuery);