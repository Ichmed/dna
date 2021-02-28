function smartlink(type, name)
{
	elem = document.querySelector('#container_' + type + '_' + name);
	
	if(elem == null)
	{
		window.location.href="/rulebook/search/" + type + "/id=" + name;
	}
	else
	{
		let cursor = elem
		
		while(cursor != null)
		{
			if(cursor.classList.contains("collapsable"))
				cursor.setAttribute("collapsed", "false");
			
			cursor = cursor.parentElement;
		}
		
		history.pushState(null, null, '#container_' + type + '_' + name);
		elem.style.backgroundColor = "orange";
		elem.style.transition = "0.3s";
		elem.scrollIntoView({ left: 0, block: 'start', behavior: 'smooth' });
		setTimeout(function(){elem.style.backgroundColor = null;}, 1000)
	}
	
	return elem;	
}

function toggle_collapse(elem)
{
	elem.setAttribute("collapsed", !((elem.getAttribute("collapsed") == 'true')));
}