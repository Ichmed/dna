document.addEventListener("DOMContentLoaded", function(event) {
    var a = document.getElementsByClassName("wikipedia_Container");
	for(i = 0; i < a.length; i++)
    {
		wiki = a[i];
    	xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function()
		{
			if (this.readyState == 4 && this.status == 200)
			{
				
				console.log(new DOMParser().parseFromString(this.responseText, "text/html"));
			}
		};
		/*var url = "https://en.wikipedia.org/w/api.php?action=parse&prop=revisions&rvprop=content&origin=*&format=jsonfm&titles=" + wiki.innerText;*/
		var url = "https://en.wikipedia.org/wiki/" + wiki.innerText + "?action=render&origin=*";
		
    	console.log(wiki.innerText);
		xhttp.open("GET", url);
    	xhttp.setRequestHeader( 'Api-User-Agent', 'Example/1.0' );
		xhttp.send();
    }
});