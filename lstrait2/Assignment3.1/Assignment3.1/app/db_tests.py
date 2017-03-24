import unittest
from app import db
from main_app import app
from model.portfolio.entries import Directory, File, Comment
from model.portfolio.repository import Repository
from model.filter import Filter
from model.parser.xml_parser import XMLParser


class DbTests(unittest.TestCase):

	def setUp(self):
		app.config['TESTING'] = True
		self.flask_app = app.test_client()

	# Test filters were added to db properly
	def test_filter_table(self):
		# get everything in query table
		filters = Filter.query.all()
		self.assertEqual(len(filters), 5)
		# earliest word added was 'shit'
		self.assertEqual(filters[0].word, 'shit')
		self.assertEqual(filters[0].replacement, 'apple')

	# Test portfolio can be re-created from db
	def test_portfolio_tables(self):
		# re-create portfolio from db
		portfolio = Repository.generate_portfolio_from_db(db)
		portfolio_xml = XMLParser('resources/data/svn_list_new.xml',
							  'resources/data/svn_log_new.xml').parse_subversion_xml()

		self.assertEqual(len(portfolio.files), len(portfolio_xml.files))
		self.assertEqual(len(portfolio.directories), len(portfolio_xml.directories))

	# test endpoint writes comment to db
	def test_writing_comment_to_db(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
									  data=dict(comment="THIS IS A TEST"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# check that comment was successfully added to database
		comment = Comment.query.filter_by(message="THIS IS A TEST", file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNotNone(comment)
		# remove comment from db
		db.session.delete(comment)
		db.session.commit()

	# test endpoint filters comment before writing to db (single filtered word)
	def test_writing_comment_to_db_filter_single(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="fuck"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# check that comment with filter applied was successfully added to database
		comment = Comment.query.filter_by(message="banana",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNotNone(comment)
		# check that comment wasn't added with filter
		comment2 = Comment.query.filter_by(message="fuck",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNone(comment2)
		# remove comment from db
		db.session.delete(comment)
		db.session.commit()

	# test endpoint filters comment before writing to db (multiple filtered word)
	def test_writing_comment_to_db_filter_multiple(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="fuck that shit"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# check that comment with filter applied was successfully added to database
		comment = Comment.query.filter_by(message="banana that apple",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNotNone(comment)
		# check that comment wasn't added with filter
		comment2 = Comment.query.filter_by(message="fuck that shit",
										   file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNone(comment2)
		# remove comment from db
		db.session.delete(comment)
		db.session.commit()

	# test endpoint filters comment before writing to db (multiple filtered word without space between)
	def test_writing_comment_to_db_filter_multiple_no_space(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="fucked that shited"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# check that comment with filter applied was successfully added to database
		comment = Comment.query.filter_by(message="bananaed that appleed",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNotNone(comment)
		# check that comment wasn't added with filter
		comment2 = Comment.query.filter_by(message="fucked that shited",
										   file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNone(comment2)
		# remove comment from db
		db.session.delete(comment)
		db.session.commit()

	# make a comment and then reply to it.
	def test_replying_comment_no_filter(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="THIS IS A TEST"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# check that comment was successfully added to database
		comment = Comment.query.filter_by(message="THIS IS A TEST",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNotNone(comment)
		# hit post endpoint to reply
		res2 = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt/' + str(comment.id),
								  data=dict(comment="REPLY TO TEST"))
		# request should have worked
		self.assertEqual(res2.status_code, 200)
		# check that comment was successfully added to database
		reply = Comment.query.filter_by(parent=comment.id).first()
		self.assertIsNotNone(reply)
		# remove comment and reply from db
		db.session.delete(comment)
		db.session.commit()
		db.session.delete(reply)
		db.session.commit()

	# make a comment, a reply, then reply to the reply
	def test_replying_reply_no_filter(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="THIS IS A TEST"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# check that comment was successfully added to database
		comment = Comment.query.filter_by(message="THIS IS A TEST",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNotNone(comment)
		# hit post endpoint to reply
		res2 = self.flask_app.post(
			'/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt/' + str(comment.id),
			data=dict(comment="REPLY TO TEST"))
		# request should have worked
		self.assertEqual(res2.status_code, 200)
		# check that comment was successfully added to database
		reply = Comment.query.filter_by(parent=comment.id).first()
		self.assertIsNotNone(reply)
		# hit post endpoint to reply to reply
		res3 = self.flask_app.post(
			'/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt/' + str(reply.id),
			data=dict(comment="REPLY TO REPLY TEST"))
		# request should have worked
		self.assertEqual(res3.status_code, 200)
		# check that comment was successfully added to database
		reply2 = Comment.query.filter_by(parent=reply.id).first()
		self.assertIsNotNone(reply2)
		# remove comment and reply from db
		db.session.delete(comment)
		db.session.commit()
		db.session.delete(reply)
		db.session.commit()
		db.session.delete(reply2)
		db.session.commit()

	# test that replies are also passed through filter
	def test_replying_comment_filter(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="THIS IS A TEST"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# check that comment was successfully added to database
		comment = Comment.query.filter_by(message="THIS IS A TEST",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNotNone(comment)
		# hit post endpoint to reply with filtered word
		res2 = self.flask_app.post(
			'/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt/' + str(comment.id),
			data=dict(comment="REPLY TO shit"))
		# request should have worked
		self.assertEqual(res2.status_code, 200)
		# check that comment was successfully added to database
		reply = Comment.query.filter_by(parent=comment.id, message="REPLY TO apple").first()
		self.assertIsNotNone(reply)
		# check comment without filter not added to database
		reply2 = Comment.query.filter_by(parent=comment.id, message="REPLY TO shit").first()
		self.assertIsNone(reply2)
		# remove comment and reply from db
		db.session.delete(comment)
		db.session.commit()
		db.session.delete(reply)
		db.session.commit()

	# Test that multiple comments can be made on a file with same message not overwritten
	def test_comment_same_message(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="THIS IS A DOUBLE TEST COM"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# hit post endpoint to write again
		res2 = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="THIS IS A DOUBLE TEST COM"))
		# request should have worked
		self.assertEqual(res2.status_code, 200)
		# check that comment was successfully added to database
		comments = Comment.query.filter_by(message="THIS IS A DOUBLE TEST COM",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').all()
		# both comments should be stored in db
		self.assertEqual(len(comments), 2)

		db.session.delete(comments[0])
		db.session.commit()
		db.session.delete(comments[1])
		db.session.commit()

	# test children field is properly tacked on after query
	def test_get_children_comment(self):
		# hit post endpoint to write
		res = self.flask_app.post('/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt',
								  data=dict(comment="THIS IS A TEST"))
		# request should have worked
		self.assertEqual(res.status_code, 200)
		# check that comment was successfully added to database
		comment = Comment.query.filter_by(message="THIS IS A TEST",
										  file='Assignment0/CS440_MP1/mazes/large_maze.txt').first()
		self.assertIsNotNone(comment)
		# hit post endpoint to reply
		res2 = self.flask_app.post(
			'/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt/' + str(comment.id),
			data=dict(comment="REPLY TO TEST"))
		# request should have worked
		self.assertEqual(res2.status_code, 200)
		# check that comment was successfully added to database
		reply = Comment.query.filter_by(parent=comment.id).first()
		self.assertIsNotNone(reply)
		# hit post endpoint to reply to reply
		res3 = self.flask_app.post(
			'/assignments/Assignment0/files/Assignment0/CS440_MP1/mazes/large_maze.txt/' + str(reply.id),
			data=dict(comment="REPLY TO REPLY TEST"))
		# request should have worked
		self.assertEqual(res3.status_code, 200)
		# check that comment was successfully added to database
		reply2 = Comment.query.filter_by(parent=reply.id).first()
		self.assertIsNotNone(reply2)

		Comment.generate_children([comment, reply, reply2])
		# assert children correctly generated
		self.assertEqual(list(comment.children)[0].id, reply.id)
		self.assertEqual(list(reply.children)[0].id, reply2.id)
		self.assertEqual(len(list(reply2.children)), 0)


		# remove comment and reply from db
		db.session.delete(comment)
		db.session.commit()
		db.session.delete(reply)
		db.session.commit()
		db.session.delete(reply2)
		db.session.commit()


if __name__ == '__main__':
	unittest.main()