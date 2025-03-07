$(function() {
    $.ajax({
        url: '/getRooms',
        type: 'GET',
        success: function(res) {
            console.log(res);
            var div = $('<div>')
                .attr('class', 'list-group')
                .append($('<a>')
                    .attr('class', 'list-group-item active')
                    .append($('<h4>')
                        .attr('class', 'list-group-item-heading')));
            var roomObj = JSON.parse(res);
            var room = '';
            $.each(roomObj, function(index, value) {
                room = $(div).clone();
                $(room).find('h4').text(value.Title);
                $(room).find('a').attr('href', '/Home/' + value.Title)
                $('.jumbotron').append(room);
            });
        },
        error: function(error) {
            console.log(error);
        }
    });
});