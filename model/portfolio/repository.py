from model.portfolio.entries import Directory, File
from model.portfolio.revision import Revision


class Repository(object):
	""" Class Representing Subversion Repository

	"""

	def __init__(self, directories, files):
		""" Constructor.

		:param directories: directories in the repository
		:param files: files in the repository
		"""
		self.directories = directories
		self.files = files
		self.assignments = self.get_assignments()		# top-level assignments in repo
		self.set_parents_and_children()					# set parents and children for all directories and files

	def get_assignments(self):
		""" Get all top-level assignments

		:return: list of all top level assignments, in order
		"""
		assignments = []
		for dir_name in self.directories.keys():
			# ignore repos that are not part of assignments
			if 'Assignment' not in dir_name:
				continue
			# top-level repos do not have / in name
			if '/' not in dir_name:
				assignments.append(self.directories[dir_name])
		# sort by name so assignments are in order
		return sorted(assignments, key=lambda assignment: assignment.name)

	def set_parents_and_children(self):
		""" Set parents and children for all entries

		"""
		# loop over all files
		for file_name in self.files.keys():
			# remove everything after last /
			parent_dir_name = file_name[:file_name.rindex('/')]
			# set parent and children
			if parent_dir_name not in self.directories.keys():
				continue
			self.files[file_name].parent = self.directories[parent_dir_name]
			self.files[file_name].parent_name = self.directories[parent_dir_name].name
			self.directories[parent_dir_name].children.append(self.files[file_name])
		# loop over all directories
		for dir_name in self.directories.keys():
			# top-level directories will not have parent
			if '/' not in dir_name:
				continue
			# remove everything after last /
			parent_dir_name = dir_name[:dir_name.rindex('/')]
			if parent_dir_name not in self.directories.keys():
				continue
			# set parent and children
			self.directories[dir_name].parent = self.directories[parent_dir_name]
			self.directories[dir_name].parent_name = self.directories[parent_dir_name].name
			self.directories[parent_dir_name].children.append(self.directories[dir_name])

	def assign_revisions(self, revisions):
		""" Helper method to assign revisions to directories and files
		"""
		for revision in revisions:
			if revision.name in self.directories.keys():
				# check revision wasn't already added
				if revision.revision not in [version.revision for version in self.directories[revision.name].versions]:
					self.directories[revision.name].versions.append(revision)
			if revision.name in self.files.keys() and revision not in self.files[revision.name].versions:
				# check revision wasn't already added
				if revision.revision not in [version.revision for version in self.files[revision.name].versions]:
					self.files[revision.name].versions.append(revision)

	@staticmethod
	def generate_portfolio_from_db(db):
		""" Use database to create svn portfolio

		:return: repository object containing data from database
		"""
		# get the files and directories from db
		directory_list = Directory.query.all()
		file_list = File.query.all()
		for directory in directory_list:
			directory.children = []
			directory.versions = []
		for file in file_list:
			file.children = []
			file.versions = []
		# transform list into a dict
		files = dict((file.name, file) for file in file_list)
		directories = dict((directory.name, directory) for directory in directory_list)
		# create repo
		portfolio = Repository(directories, files)
		# assign revisions, query db to get all
		revisions = Revision.query.all()
		portfolio.assign_revisions(revisions)
		# return complete portfolio
		return portfolio

