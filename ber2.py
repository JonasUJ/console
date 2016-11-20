import sys
from codecs import open as copen

class dictdb (dict):

	separator = '{#}'
	kvSep = '{|}'
	writeFormat = '%s%s%s%s%s' % (separator, '%s', kvSep, '%s', separator)
		
	def __init__(self, file, *args, **kwargs):
		self.file = file if file[1] == ':' else '%s/%s' % ('/'.join(sys.argv[0].split('/')[:-1]), file)
		with copen(file, 'r', encoding='utf-8') as f:
			self.update(dict([(x.split(self.kvSep, 1)[0], x.split(self.kvSep, 1)[1]) for x in ''.join(f.read()).split(self.separator) if x != '' and x != '\n']))
		self.update(dict(*args, **kwargs))		

	def save(self):
		with copen(self.file, 'w', encoding='utf-8') as f:
			f.writelines(''.join([self.writeFormat % kv for kv in list(self.items())]))