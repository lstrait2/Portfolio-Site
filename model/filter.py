from app import db


class Filter(db.Model):
	""" Class to represent filter for comments
	"""
	word = db.Column(db.String(50), primary_key=True)
	replacement = db.Column(db.String(50))

	def __init__(self, word, replacement):
		self.word = word
		self.replacement = replacement