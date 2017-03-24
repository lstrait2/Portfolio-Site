import unittest

from model.portfolio.revision import Revision
from model.portfolio.entries import Directory, File
from model.portfolio.repository import Repository


class PortfolioTests(unittest.TestCase):

	def setUp(self):
		self.dir = Directory('Assignment5.0', 1, '04/12/17', 'lstrait2')
		self.file = File('Assignment5.0/f.txt', 2, '04/13/17', 'lstrait2', 25)
		revision = Revision('17', '04/13/16', 'lstrait2', 'this is a commit', '17')
		self.file.versions.append(revision)
		self.dir.versions.append(revision)
		# constructor a repo from file and directory
		self.dirs = dict()
		self.dirs[self.dir.name] = self.dir
		self.files = dict()
		self.files[self.file.name] = self.file
		self.repo = Repository(self.dirs, self.files)

	# test repository and child constructors correctly initalize
	def test_constructors(self):
		# build a dictionary
		self.assertEqual(self.dir.name, 'Assignment5.0')
		self.assertEqual(self.dir.revision, 1)
		self.assertEqual(self.dir.author, 'lstrait2')
		# ensure fields inherited from Entry superclass correctly set
		self.assertEqual(self.dir.summary, "")
		# build a file
		self.assertEqual(self.file.size, 25)
		# ensure fields inherited from Entry superclass correctly set
		self.assertEqual(self.file.summary, "")
		# check repo constructor correctly set fields
		self.assertEqual(self.repo.directories, self.dirs)
		self.assertEqual(self.repo.files, self.files)
		self.assertEqual(self.repo.assignments, [self.dir])

	# check file names correctly remove path
	def test_get_file_name(self):
		# function should strip path
		self.assertEqual(self.file.get_file_name(), 'f.txt')

	# check file names correctly remove path for longer path
	def test_get_file_name_larger(self):
		file = File('Dir1/Dir2/Dir3/Dir4/f.txt', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file.get_file_name(), 'f.txt')

	# test stripping path when none exists
	def test_get_file_name_no_path(self):
		file = File('f.txt', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file.get_file_name(), 'f.txt')

	# check getting top level assignments works
	def test_get_assignments(self):
		assignments = self.repo.get_assignments()
		# dir should be an assignment
		self.assertEqual(assignments, [self.dir])

	# check creating "tree" works
	def test_set_parents_and_children(self):
		self.repo.set_parents_and_children()
		# dir should be parent of file
		self.assertEqual(self.file.parent, self.dir)
		# file should be child of dir
		self.assertEqual(set(self.dir.children), set([self.file]))
		# dir should have no parents
		self.assertEqual(self.dir.parent, None)

	# test creating "tree" works no edges
	def test_set_parents_and_children(self):
		# create file and directory not connected
		dir = Directory('Assignment5.0', 1, '04/12/17', 'lstrait2')
		file = File('Assignment6.0/f.txt', 2, '04/13/17', 'lstrait2', 25)
		dirs = {dir.name: dir}
		files= {file.name: file}
		repo = Repository(dirs, files)
		repo.set_parents_and_children()
		# neither file nor dir has parent
		self.assertEqual(file.parent, None)
		self.assertEqual(dir.parent, None)
		# neither file nor dir has children
		self.assertEqual(file.children, [])
		self.assertEqual(dir.children, [])


	# check last commit works
	def test_last_commit(self):
		# add a new commit
		revision = Revision('18', '04/14/16', 'lstrait2', 'this is a new commit', '18')
		self.file.versions.append(revision)
		self.dir.versions.append(revision)
		# the new commit should be last commit for both
		self.assertEqual(self.file.get_last_commit(), revision)
		self.assertEqual(self.dir.get_last_commit(), revision)

	# check last commit works file nested in directory
	def test_last_commit_nested(self):
		# add a new commit to file but not directory
		revision = Revision('18', '04/14/16', 'lstrait2', 'this is a new commit', '18')
		self.file.versions.append(revision)
		# this commit should be commit for directory as well
		self.assertEqual(self.dir.get_last_commit(), revision)

	# check summary is last commit message
	def test_get_summary(self):
		# both file and dir have same commit message
		self.assertEqual(self.file.get_summary(), "this is a commit")
		self.assertEqual(self.dir.get_summary(), "this is a commit")


	"""
	All tests below test that file types are correctly classified as 'code', 'image', 'test', or 'resource'
	"""

	def test_get_file_type_python(self):
		file2 = File('Assignment5.0/f.py', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'code')

	def test_get_file_type_java(self):
		file2 = File('Assignment5.0/f.java', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'code')

	def test_get_file_type_js(self):
		file2 = File('Assignment5.0/f.js', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'code')

	def test_get_file_type_css(self):
		file2 = File('Assignment5.0/f.css', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'code')

	def test_get_file_type_html(self):
		file2 = File('Assignment5.0/f.html', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'code')

	def test_get_file_type_python_test(self):
		file2 = File('Assignment5.0/f_test.py', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'test')

	def test_get_file_type_java_test(self):
		file2 = File('Assignment5.0/fTests.java', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'test')

	def test_get_file_type_image_jpg(self):
		file2 = File('Assignment5.0/hello.jpg', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'image')

	def test_get_file_type_image_jpeg(self):
		file2 = File('Assignment5.0/hello.jpeg', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'image')

	def test_get_file_type_image_png(self):
		file2 = File('Assignment5.0/hello.png', 2, '04/13/17', 'lstrait2', 25)
		self.assertEqual(file2.get_file_type(), 'image')

	def test_get_file_type_txt(self):
		self.assertEqual(self.file.get_file_type(), 'resource')


if __name__ == '__main__':
	unittest.main()