import sqlite3, os


for template_name in os.listdir('templates'):

	if not os.path.isfile('templates/' + template_name): continue
	source = sqlite3.connect('_base.db')
	cursor_s = source.cursor()
	cursor_s.execute('SELECT * FROM `{}`'.format(template_name))


	template = open('templates/' + template_name).read()

	fields = ['ID'] + [x.split(' ')[0] for x in template.split('\n') if x.startswith('`')]

	target = sqlite3.connect('base.db')
	cursor_t = target.cursor()

	q = 'INSERT INTO `{}` ({}) VALUES ({})'.format(template_name, ','.join(fields), ','.join(['?' for i in range(len(fields))]))

	cursor_t.executemany(q, cursor_s)

	target.commit()
