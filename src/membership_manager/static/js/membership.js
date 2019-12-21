
window.addEventListener("load",  function(){
if(window.location.href.indexOf("/change/") === -1){
    (function($){
         $("#changelist-filter").css(
         {'position':  'relative', 'width': '100%',
         "display": "inline-flex"
         }     );
         $("#changelist-form .results").css(
         {"margin-right": 0, "overflow-x": "scroll"  }  );
        $( "#changelist-filter" ).wrap( "<div class='hiddenfilters'></div>" );
        $( "#changelist-filter h2" ).insertBefore("#changelist-filter");
        $( "#changelist-filter" ).hide();
        $(".hiddenfilters h2").on('click', function(){
            $( "#changelist-filter" ).toggle();
        });


     })(django.jQuery);
}
 });