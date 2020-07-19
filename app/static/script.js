window.onload=function() {
	form = document.getElementById("card-form")
	success_btn = document.getElementById("correct")
	failure_btn = document.getElementById("incorrect")
	
	form.addEventListener("submit", function() {
		console.log('hello')
   		success_btn.setAttribute("disabled", "")
    		failure_btn.setAttribute("disabled", "")
	})
}
