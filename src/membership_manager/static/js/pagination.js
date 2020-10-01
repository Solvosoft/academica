(function($){
    $.fn.gentellelapaginate = function(){
        var initpagination = function(item, pagdiv, prefix){

        var paginate = $(item);
        var paginateChildren = paginate.children();
        var totalItems = paginateChildren.length;
        var itemsPerPage = 5;
        var totalPages = Math.ceil(totalItems / itemsPerPage);

        if(totalItems > itemsPerPage) {

            var tempPage, startItem, lastItemm, currentPage;

            for(var page = 1; page <= totalPages; page++) {

                tempPage = $('<div id="'+prefix+'-item-page-'+page+'" class="item-page'+(page === 1 ? ' active' : '')+'" />');
                startItem = (page-1) * itemsPerPage;
                lastItem = startItem + itemsPerPage;
                if(lastItem >= totalItems) {
                    lastItem = totalItems;
                }
                while (startItem < lastItem) {
                    paginateChildren.eq(startItem).appendTo(tempPage);
                    startItem++;
                }

                paginate.append(tempPage);

                if(page === 1) {
                    currentPage = $('#'+prefix+'-item-page-'+page, paginate);
                }
            }

            $(pagdiv).twbsPagination({
                totalPages: totalPages,
                visiblePages: 5,
                first: 'Inicio',
                prev: 'Prev',
                next: 'Sig',
                last: 'Último',
                onPageClick: function (event, page) {
                    currentPage.hide();
                    currentPage = $('#'+prefix+'-item-page-'+page, paginate);
                    currentPage.show();
                }
            });
        }
        }

    $(this).each(function(index, element){
        var content = $(element).find(".paginate-content");
        var pagui = $(element).find(".gppagination");
        var prefix = $(element).data('prefix');
        initpagination(content, pagui, prefix);

        });
    }

})(jQuery)