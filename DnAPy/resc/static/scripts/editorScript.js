function insertEditor(name, type)
{
	var container = document.getElementById("container_" + type + "_" + name);

	xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function()
	{
		if (this.readyState == 4 && this.status == 200)
		{
			container.innerHTML = this.responseText;
			container.style = "opacity: 1;";
			updateBobbles(name + "_SkillSelector");
			
			
			autosize(document.querySelectorAll('textarea'));
		}
	};
	var url = "/api/editor?type=" + type + "&ID=" + name;
	xhttp.open("GET", url);
	xhttp.send();

}

function save(name, type, swapOnSave)
{
	save(name, type, swapOnSave, true);
}

function save(name, type, swapOnSave, clearOnSave)
{
	var editor = document.getElementById("editor_" + type + "_" + name);

	if(name == "null")
		var url = "/api/add/";
	else
		var url = "/api/update/";

	url += type + "?";

	var matches = editor.getElementsByClassName("input_content");
	for (var i = 0; i < matches.length; i++)
	{
		url += matches[i].name + "=";
		url += matches[i].value + "&";
	}

	url = url.replace(/%/g, "%25").replace(/\n/g, "%0A").replace(/#/g, "%23").replace(/\+/g, "%2B");
	url = url.replace(/\n/g, "%0D");

	xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function()
	{
		if (this.readyState == 4 && this.status == 200)
		{
			if (swapOnSave == true)
			{
				xhttpContainer = new XMLHttpRequest();
				xhttpContainer.onreadystatechange = function()
				{
					if (this.readyState == 4 && this.status == 200)
					{
						var container = document.getElementById("container_" + type + "_" + name);
						var response = new DOMParser().parseFromString(this.responseText, "text/html").getElementById("container_" + type + "_" + name);
						console.log("container_" + type + "_" + name);
						container.innerHTML = response.innerHTML;

					}
				};
				var url = "/search/" + type + "?ID=" + name;
				
				xhttpContainer.open("GET", url);
				xhttpContainer.send();
			}

			if (clearOnSave)
				for (var i = 0; i < matches.length; i++)
				{
					url += matches[i].value = "";
				}
		}
	};
	console.log(url);
	xhttp.open("GET", url);
	xhttp.send();

}

function setSelector(containerName, value)
{
	var container = document.getElementById(containerName);
	var dataField = document.getElementById(containerName + "_data");
	console.log(containerName + "_" + dataField.value);
	document.getElementById(containerName + "_" + dataField.value).style.opacity = "";
	dataField.value = value;
	document.getElementById(containerName + "_" + dataField.value).style.opacity = 1.0;
}

document.addEventListener("DOMContentLoaded", function(event)
{
	updateBobbles("null_SkillSelector");
});

function updateBobbles(name)
{
	if (document.getElementById(name + "_cost") == null)
		return;
	var cost = parseInt(document.getElementById(name + "_cost").value);
	var skill = document.getElementById(name + "_skill_data").value;

	var cont = "";
	if (cost < -1)
		cost = document.getElementById(name + "_cost").value = -1;

	if (cost == -1)
		cont = '<img src="/symbols/costUnavailable.png">';
	else if (cost == 0)
		cont = '<img src="/symbols/costFree.png">';
	else
	{
		for (i = 0; i < cost; i++)
		{
			cont += '<img src="/symbols/bobble' + skill + '.png">';
		}
	}
	var leveling = document.getElementById(name + "_leveling_data").value;
	if (leveling != 'None')
		cont += '<img src="/symbols/upgrade' + leveling + '.png">';
	document.getElementById(name + '_bobbles').innerHTML = cont;
}