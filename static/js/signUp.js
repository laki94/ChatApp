$(function(){
	$('#btnSignUp').click(function(){

		$.ajax({
			url: '/signUp',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
				window.location.replace('/signUp')
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});