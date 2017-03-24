from app import db
from model.filter import Filter


class Comment(db.Model):
	""" Class to represent Comment on file in subversion repo
	"""
	id = db.Column(db.Integer, primary_key=True)
	# one-to-many relationship between file and comment
	file = db.Column(db.String(200), db.ForeignKey('file.name'))
	# one-to-many relationship between file and comment
	parent = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
	message = db.Column(db.String(200))

	def __init__(self, file, parent, message):
		""" Constructor

		:param file: file comment is on
		:param parent: parent comment for the comment
		:param message: content of the comment
		"""
		self.file = file
		self.parent = parent
		self.message = message
		self.children = []

	def apply_filter(self):
		""" Apply filter stored in portfolio db to this comment
		"""
		word_filter = {filter_word.word: filter_word.replacement for filter_word in Filter.query.all()}
		# replace filter words with their replacements in comment message
		for word in word_filter.keys():
			self.message = self.message.replace(word, word_filter[word])

	@staticmethod
	def generate_children(comments):
		""" Generate children for comments
		"""
		for comment in comments:
			# get all comment from db with whose parent is current comment
			comment.children = reversed(Comment.query.filter_by(parent=comment.id).all())


# directory must be defined in same file as comment and file or circular imports exist
class Directory(db.Model):
	""" Class to represent a Dictionary in Subversion Repository.
	"""

	name = db.Column(db.String(200), primary_key=True)
	revision = db.Column(db.Integer)
	date = db.Column(db.String(200))
	author = db.Column(db.String(200))
	date = db.Column(db.String(200))
	summary = db.Column(db.String(200))
	# one-to-many relationship between dir and dir
	parent_name = db.Column(db.String(200), db.ForeignKey('directory.name'), nullable=True)

	def __init__(self, name, revision, date, author):
		""" Constructor

		:param name: Name of the directory
		:param revision: Current revision number for directory
		:param date: Date of last commit
		:param author: Author of last commit
		"""
		self.name = name
		self.revision = revision
		self.date = date
		self.author = author
		self.summary = ""  # Summary of entry is last commit message
		self.versions = []  # history of all revisions of entry
		self.parent = None  # parent directory of entry
		self.children = []

	def get_last_commit(self):
		""" Get the last commit made to this directory

		:return: Revision Object representing last commit
		"""
		# sort the revisions for this directory by date
		last_commit = sorted(self.versions, key=lambda revision: revision.date)[-1]
		# if the directory is non-empty, check commits for children
		if len(self.children) != 0:
			for child in self.children:
				child_commit = child.get_last_commit()
				# if child commit occurred after last_commit, it is now last_commit
				if child_commit is not None and child_commit.date > last_commit.date:
					last_commit = child_commit
		return last_commit

	def get_directory_name(self):
		""" strip parent directories from name

		:return: base name of the directory
		"""
		return self.name[self.name.rindex('/'):][1:] + '/'

	def get_summary(self):
		""" Get summary for this entry

		:return: Last commit message for this entry
		"""
		return self.get_last_commit().msg


# must defined File in same file as directory or get circular imports
class File(db.Model):
	""" Class to represent File in Subversion Repository
	"""
	name = db.Column(db.String(200), primary_key=True)
	revision = db.Column(db.Integer)
	date = db.Column(db.String(200))
	author = db.Column(db.String(200))
	date = db.Column(db.String(200))
	summary = db.Column(db.String(200))
	# one-to-many relationship between dir and files
	parent_name = db.Column(db.String(200), db.ForeignKey('directory.name'))
	size = db.Column(db.Integer)

	def __init__(self, name, revision, date, author, size):
		""" Constructor.

		:param name: Name of file
		:param revision: Current revision of file
		:param date: Date of last commit
		:param author: Author of last commit
		:param size: Size of the file
		"""
		self.name = name
		self.revision = revision
		self.date = date
		self.author = author
		self.summary = ""  # Summary of entry is last commit message
		self.versions = []  # history of all revisions of entry
		self.parent = None  # parent directory of entry
		self.size = size
		self.children = []	# children should always be empty for files, needed for templating

	def get_last_commit(self):
		""" Get last commit of this file

		:return: Revision object representing last commit
		"""
		if len(self.versions) == 0:
			return None
		# return oldest commit
		return sorted(self.versions, key=lambda revision: revision.date)[-1]

	def get_file_name(self):
		""" String the leading path and return only filename

		:return: base filename
		"""
		if '/' not in self.name:
			return self.name
		return self.name[self.name.rindex('/'):][1:]

	def get_file_type(self):
		""" return the type of file

		:return:a type in ['code', 'test', 'image', 'resource']
		"""
		name = self.get_file_name()
		if 'test' in name or 'Tests' in name:
			return 'test'
		elif '.py' in name or '.java' in name or '.css' in name or '.js' in name or '.htm' in name:
			return 'code'
		elif '.png' in name or '.jpg' in name or '.jpeg' in name:
			return 'image'
		else: return 'resource'

	def get_summary(self):
		""" Get summary for this entry

		:return: Last commit message for this entry
		"""
		return self.get_last_commit().msg