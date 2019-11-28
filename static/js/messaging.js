 $(document).ready(function(){
       var socket = io.connect('http://' + document.domain + ':' + location.port );
      socket.on( 'connect', function() {
        socket.emit( 'join', {
            room_name: location.pathname
        } );
        var form = $( 'form' ).on( 'submit', function( e ) {
          e.preventDefault()
          let user_input = $( 'input.message' ).val()
          if (user_input !== '')
              socket.emit( 'my event', {
                message : user_input
              } );
          $( 'input.message' ).val( '' ).focus()
        } );
      } );
      socket.on( 'my response', function( msg ) {
        console.log( msg )
          $( 'div.message_holder' ).append( '<p><b style="color: #000">'+msg.user_name+'</b> '+msg.message+'</p>' )
          $( 'div.message_holder' ).animate({scrollTop: $( 'div.message_holder' ).height()}, 0)
      })
      });