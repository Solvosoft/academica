django.jQuery(function(){
	function process_td(name, list, css_class, clean){
		if(clean == true){
			$('#'+name+" td").removeClass(name+"_active");
			$('#'+name+" td").removeClass(name+"_selected");
		}
		for(var x=0; x<list.length; x++){
			$("#"+name+" #"+list[x]).parent().addClass(css_class);
		}
	}
	function process_table(obj){
		process_td(obj.type, obj.hours, obj.type+"_active", true);
		process_td(obj.type, obj.selected, obj.type+"_selected", false);
	}
	
	function process_type($, url, tid){
   	 	id = $(tid).val();
		$.ajax({
			dataType: "json",
			url: url+"?pk="+id,
			success: process_table
		});
		
	}
$(function(){
    $(function(){
        $("#id_classroom_on_deck").bind('added', function() {
			process_type($, classroom_schedule_url, "#id_classroom");
  		});
        $("#id_profesor_on_deck").bind('added', function() {
			process_type($, profesor_schedule_url, "#id_profesor");
  		});  		
  		
  		process_type($, profesor_schedule_url, "#id_profesor");
		process_type($, classroom_schedule_url, "#id_classroom");
    });
});
	
	
});
