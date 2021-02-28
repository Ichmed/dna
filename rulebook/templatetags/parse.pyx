from shlex import split
from .md import create_widget

def parse(text):
	result = ""
	widget = ""
	cdef int found = 0
	cdef int parenthesis = 0
	cdef int i = 0
	cdef int l = len(text)
	cdef int len_widget
	while i < l:
		if parenthesis == 0 and text[i] == "$":
			#i += 1
			if text[i + 1] == '$':
				result += '$'
				i += 2
				continue
			widget = ""
			found = 1
		elif found:
			widget += text[i]
			if text[i] == "(":
				parenthesis += 1
			elif text[i] == ")":
				parenthesis -= 1
				if parenthesis == 0:
					len_widget = len(widget)
					arg = widget[1:len_widget-1]
					result += create_widget(split(arg))
					found = 0
				
		else:
			result += text[i]
		#print(result)
		i += 1

	return result