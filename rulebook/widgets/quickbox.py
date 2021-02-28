import query_helper
import markdown2 as mk

def build(text):
	return {"quickbox": '<div class="quickbox"><h1>Quickbox</h1><div class=text>' + mk.markdown(text) + '</dvi></div>'}, []