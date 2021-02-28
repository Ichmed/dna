cimport cython

cdef dict widget_cache = {}

cdef list stack = []

cdef class WidgetCacheObject:
	cdef list dependends
	cdef int valid
	cdef str content
	
	def __init__(self):
		self.dependends = []

	@cython.boundscheck(False)  # Deactivate bounds checking
	@cython.wraparound(False)   # Deactivate negative indexing.
	cdef invalidate(self):
		if not self.valid: return
		self.valid = 0

		#invalidate all dependends
		cdef int i = 0
		cdef int length = len(self.dependends)
		cdef str key
		cdef WidgetCacheObject w
		for i in range(length):
			key = self.dependends[i]
			print("invalidating", key)
			if key in widget_cache:
				w = widget_cache[key]
				w.invalidate()

		self.dependends = []

cdef _get(str key):
	if not key in widget_cache:
		return None
	
	cdef WidgetCacheObject w = widget_cache[key]
	if not w.valid:
		return None
	
	return w.content

def get(str key):
	return _get(key)

cdef _put(str key, str value):
	cdef WidgetCacheObject w
	cdef dict cache = widget_cache
	if not key in cache:
		w = WidgetCacheObject()
		cache[key] = w
	else:
		w = cache[key]
	if value != None: w.content = value
	if(len(stack) > 1): 
		w.dependends.append(stack[-2])
	w.valid = 1

def put(str value=None):
	return _put(stack[-1], value)

cdef _invaldiate(str key):
	cdef dict cache = widget_cache
	if not key in cache:
		return
	cdef WidgetCacheObject w = cache[key]
	w.invalidate()

def invalidate(str key):
	print("invalidating", key)
	return _invaldiate(key)

def push(key):
	stack.append(key)

def pop():
	del stack[-1]