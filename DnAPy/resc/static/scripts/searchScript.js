function search(dropdownId, queryId, resultsId)
{
	xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function()
	{
		if (this.readyState == 4 && this.status == 200)
		{
			document.getElementById(resultsId).innerHTML = this.responseText;
			/*console.log(this.responseText);*/
		}
	};
	var q = document.getElementById(dropdownId).value + "?" + document.getElementById(queryId).value;
	/*if(document.getElementById(dropdownId).value == "abilities") url += " + parent= ";*/
	window.history.pushState("/search/" + q, "Title", "/search/" + q);
	if(document.getElementById(dropdownId).value == 'abilities' && !q.includes("parent")) q += "+ parent=";	
	xhttp.open("GET", "/api/search/compile/" + q);
	xhttp.send();
}