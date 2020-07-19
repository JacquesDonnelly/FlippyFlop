window.onload=function() {
	form = document.getElementById("card-form")
	success_btn = document.getElementById("correct")
	failure_btn = document.getElementById("incorrect")
	
	form.addEventListener("click", function(e) {
		if ( form.getAttribute('attempted') == 'true' ){
			e.preventDefault()
		}
		else {
			form.setAttribute('attempted', 'true')
		}
	})
}
