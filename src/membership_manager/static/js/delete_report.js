(function(){

  $(".delete").on("click", function(e){

    var redirecturl =  $(this).data('url');

    $.ajax({
      url: $(this).data('delete'),
      type : "DELETE",
      headers: {'X-CSRFToken': getCookie('csrftoken') },
      dataType : 'json',
      data: {'pk': $(this).data('id')},
      success : function(result) {location.href = redirecturl; },
      error: function(xhr, resp, text) {
          console.log(xhr, resp, text);
      }
    });
  });

})(jQuery);
