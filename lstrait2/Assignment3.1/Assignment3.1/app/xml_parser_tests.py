import unittest

from model.parser.xml_parser import XMLParser

class XMLParserTests(unittest.TestCase):

	def setUp(self):
		# Run tests with my svn data, added Junk repo with manually inserted edge cases
		self.parser = XMLParser('resources/data/svn_list.xml', 'resources/data/svn_log.xml')

	def test_parser_constructor(self):
		# check that parser is initialized correctly
		self.assertEqual(self.parser.list_file, 'resources/data/svn_list.xml')
		self.assertEqual(self.parser.log_file, 'resources/data/svn_log.xml')
		# repo should initially be empty until parser is run
		self.assertEqual(self.parser.svn_repo, None)

	# test that parse_xml_list parses all files and directories and stores all data
	def test_parse_xml_list(self):
		repo = self.parser.parse_xml_list()
		# 83 directories and 273 files in my 242 repo
		self.assertEqual(len(repo.directories), 83)
		self.assertEqual(len(repo.files), 273)
		# data should be correct parsed for files
		maze_file = repo.files['Assignment0/CS440_MP1/mazes/large_maze.txt']
		self.assertEqual(maze_file.size, '1406')
		self.assertEqual(maze_file.revision, '804')
		self.assertEqual(maze_file.author, 'lstrait2')
		# data should be parsed for directories
		maze_dir = repo.directories['Assignment0']
		self.assertEqual(maze_dir.revision, '1474')
		self.assertEqual(maze_dir.author, 'lstrait2')
		self.assertEqual(maze_dir.date, '2017-01-29T20:05:54.824247Z')

	# test that top level repos are correctly extracted
	def test_top_level_repos(self):
		repo = self.parser.parse_subversion_xml()
		# There are 7 top level assignments in my 242 repo
		self.assertEqual(len(repo.assignments), 7)
		self.assertIn('Assignment1.2', [assignment.name for assignment in repo.assignments])
		self.assertIn('Assignment0', [assignment.name for assignment in repo.assignments])

	# test committs appear for a file with only one total commit
	def test_all_commits_appear_single_file(self):
		repo = self.parser.parse_subversion_xml()
		pawn_file = repo.files['Assignment1.0/src/pieces/Pawn.java']
		# this file was only committed once, should only have 1 version
		self.assertEqual(len(pawn_file.versions), 1)
		# this version should match current version of file
		self.assertEqual(pawn_file.versions[0].revision, pawn_file.revision)
		# test date of commit is correct
		self.assertEqual(pawn_file.versions[0].date, '2017-02-05T21:55:51.557337Z')

	# test commits appear for a directory with only one total commit
	def test_all_commits_appear_single_directory(self):
		repo = self.parser.parse_subversion_xml()
		piece_dir = repo.directories['Assignment1.0/src/pieces']
		# this directory was only committed once, should only have 1 version
		self.assertEqual(len(piece_dir.versions), 1)
		# this version should match current version of directory
		self.assertEqual(piece_dir.versions[0].revision, piece_dir.revision)
		# test date of commit is correct
		self.assertEqual(piece_dir.versions[0].date, '2017-02-05T21:55:51.557337Z')

	# test all commits appear for a file with multiple commits
	def test_all_commits_appear_multiple_file(self):
		repo = self.parser.parse_subversion_xml()
		iml_file = repo.files['Assignment2.1/Assignment2.1/.idea/Assignment2.1.iml']
		# this file was only committed twice, should have 2 version
		self.assertEqual(len(iml_file.versions), 2)
		# top version should match current version
		self.assertEqual(iml_file.versions[0].revision, iml_file.revision)
		# second version should be older than current
		self.assertLess(iml_file.versions[1].revision, iml_file.revision)

	# test all commits appear for a directory with multiple commits
	def test_all_commits_appear_multiple_directory(self):
		repo = self.parser.parse_subversion_xml()
		assign_dir = repo.directories['Assignment2.1/Assignment2.1']
		# this file was only committed twice, should have 2 version
		self.assertEqual(len(assign_dir.versions), 2)
		# second version should be older than current
		self.assertLess(assign_dir.versions[1].revision, assign_dir.revision)

	# test all commits appear for a file that was merged
	def test_all_commits_appear_with_merges(self):
		repo = self.parser.parse_subversion_xml()
		test_file = repo.files['Assignment1.0/src/test/PieceTests.java']
		# should be 3 total commits
		self.assertEqual(len(test_file.versions), 3)
		# revision 3477 was the merge, should be in versions
		self.assertIn('3477', [version.revision for version in test_file.versions])
		# test date for merge commmit is correct.
		self.assertEqual(test_file.versions[0].date, '2017-02-06T22:20:35.294775Z')

	# test a single commit with many files is in all files version array
	def test_revision_multiple_files(self):
		repo = self.parser.parse_subversion_xml()
		# commit 6182 including 3 files, should be included in all 3 file's versions
		file1 = repo.files['Assignment2.1/Assignment2.1/view/actor_views.py']
		file2 = repo.files['Assignment2.1/Assignment2.1/view/movie_views.py']
		file3 = repo.files['Assignment2.1/Assignment2.1/view/util.py']
		self.assertIn('6182', [version.revision for version in file1.versions])
		self.assertIn('6182', [version.revision for version in file2.versions])
		self.assertIn('6182', [version.revision for version in file3.versions])

	# test a single commit with only 1 file is included in version array
	def test_revision_single_file(self):
		repo = self.parser.parse_subversion_xml()
		dir1 = repo.directories['Assignment3.0']
		# commit 6705 included only 1
		self.assertIn('6705', [version.revision for version in dir1.versions])
		# commit 6705 should not be in any other file or directory versions
		for file in repo.files.values():
			self.assertNotIn('6705', [version.revision for version in file.versions])
		for dir in repo.directories.values():
			if dir.name != 'Assignment3.0':
				self.assertNotIn('6705', [version.revision for version in dir.versions])

	# deleted files should appear in log, but not in current repo
	def test_deleted_files_not_in_repo(self):
		repo = self.parser.parse_subversion_xml()
		# Assignment2.1/Assignment2.1/Assignment2.1ManualTestingandReport.pdf was deleted in commit 6244
		self.assertNotIn('Assignment2.1/Assignment2.1/Assignment2.1ManualTestingandReport.pdf', repo.files.keys())

	# Merged files should correctly appear in repo
	def test_merged_files_appear_in_repo(self):
		repo = self.parser.parse_subversion_xml()
		# Assignment1.0/src/test/PieceTests.java was merged in commit 6244
		self.assertIn('Assignment1.0/src/test/PieceTests.java', repo.files.keys())


if __name__ == '__main__':
	unittest.main()