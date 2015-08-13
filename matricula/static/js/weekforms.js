(function($){
	weeks = {};	
	function addHour(name, value){
		if(weeks.hasOwnProperty(name)){
			if(weeks[name].indexOf(value) <= -1){
				weeks[name].push(value);
			}
		}else{
			weeks[name] = [value];
		}
		$("input[name='"+name +"']").val(weeks[name].join(";"));
	}
	function delHour(name, value){
		if(weeks.hasOwnProperty(name)){
			index = weeks[name].indexOf(value);
			if( index > -1){
				//del weeks[name][index]
				weeks[name].splice(index, 1);
				$("input[name='"+name +"']").val(weeks[name].join(";"));
			}
		}
	}	
	$(document).ready(function (){
		var $ = django.jQuery; 
		$(".week_input").each(function(x,y){
			//if (!weeks.hasOwnProperty($(y).attr("name"))){
				var value = $(y).val().split(';');
				var name = $(y).attr("name");
				if(!value[0] == ""){
					weeks[name] = value;
					$(value).each(function(y,t){
						$("#"+name + " #"+t).parent().addClass("hour_selected");
					});
				}
			//}
		});
		
		
		$(".hour").on( "mouseenter",
			function(evt){
				if (evt.ctrlKey){
				me = $(this);
				if (me.hasClass("hour_selected")){
					me.removeClass("hour_selected");
					delHour(me.closest("table").attr("name"), $(this).find("span").attr("id"));
				}else{
					me.addClass("hour_selected");
					addHour(me.closest("table").attr("name"), $(this).find("span").attr("id"));
					//alert($(this).find("span").attr("id"));
				}
			 }
			}
			
		);
	}
  )}
)(django.jQuery);
