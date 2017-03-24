from app import db


class Revision(db.Model):
	""" Object to represent svn revision

	"""
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200),)
	date = db.Column(db.String(200))
	author = db.Column(db.String(200))
	msg = db.Column(db.String(200))
	revision = db.Column(db.Integer)
	#TODO: foreign key relationship w/ name

	def __init__(self, name, date, author, msg, revision):
		""" Constructor

		:param name: Name of entry of revision
		:param date: Date of revision
		:param author: Author of revision
		:param msg: Commit message
		:param revision: revision number
		"""
		self.name = name
		self.date = date
		self.author = author
		self.revision = revision
		self.msg = msg