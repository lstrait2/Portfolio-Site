from flask import Blueprint, render_template, abort, request
from model.portfolio.entries import Comment
from app import db

def construct_portfolio_blueprint(portfolio):
	""" Blueprint to create routes for portfolio site

	:param portfolio: portfolio data created by XMLParser
	:return: blueprint with registered routes
	"""

	portfolio_blueprint = Blueprint('portfolio_blueprint', __name__)

	@portfolio_blueprint.route('/', methods=['GET'])
	def index():
		""" render template for index of site. Use Jinja to dynamically display assignment data

		:return: HTML rendering
		"""
		return render_template('index.html', portfolio=portfolio.assignments)

	@portfolio_blueprint.route('/assignments/<string:assignment_name>', methods=['GET'])
	def get_project(assignment_name):
		""" render template for assignment page. Use Jinja to dynamically display assignment data

		:param assignment_name: assignment to display
		:return: HTML rendering of assignment page, or 400 error if assignment_name doesn't exist
		"""
		assignments = filter(lambda assignment: assignment.name == assignment_name, portfolio.assignments)
		related_assignments = filter(lambda assignment: '.' in assignment_name and assignment_name != assignment.name and '.' in assignment.name
									and assignment.name[assignment.name.rindex('.') - 1] == assignment_name[assignment_name.rindex('.') - 1], portfolio.assignments)
		if len(assignments) == 0:
			abort(400)
		return render_template('assignment_page.html', assignment=assignments[0], related_assignments=related_assignments)

	@portfolio_blueprint.route('/assignments/<string:assignment_name>/files/<path:file_name>', methods=['GET'])
	def get_file(assignment_name, file_name):
		""" render template for file page. Use Jinja to dynamically display file data

		:param assignment_name: name of the assignment the file is in
		:param file_name:name of the file
		:return: HTML rendering of file page, or 400 error if file_name or assignment_name doesn't exist
		"""
		assignments = filter(lambda assignment: assignment.name == assignment_name, portfolio.assignments)
		if len(assignments) == 0 or file_name not in portfolio.files.keys():
			abort(400)
		# get all comments for the file
		comments = Comment.query.filter_by(file=file_name).all()
		Comment.generate_children(comments)
		# pass only top level comments
		comments = [comment for comment in comments if comment.parent is None]
		return render_template('file_page.html', file=portfolio.files[file_name], assignment=assignments[0], comments=reversed(comments))

	@portfolio_blueprint.route('/assignments/<string:assignment_name>/files/<path:file_name>', methods=['POST'])
	def post_comment(assignment_name, file_name):
		""" post comment and re-render file page.

		:param assignment_name: name of assignment the file is in
		:param file_name: name of the file
		:return: HTML rendering of file page, or 400 error if file_name or assignment_name doesn't exist
		"""
		# grab user input from submitted form
		comment_data = request.form['comment']
		comment = Comment(file_name, None, comment_data)
		# apply filter to comment
		comment.apply_filter()
		# propogate changes to db
		db.session.add(comment)
		db.session.commit()
		# re-display the file page.
		return get_file(assignment_name, file_name)

	@portfolio_blueprint.route('/assignments/<string:assignment_name>/files/<path:file_name>/<int:comment_id>', methods=['POST'])
	def post_reply(assignment_name, file_name, comment_id):
		""" post comment and re-render file page.

		:param assignment_name: name of assignment the file is in
		:param file_name: name of the file
		:param comment_id: id of parent comment
		:return: HTML rendering of file page, or 400 error if file_name or assignment_name doesn't exist
		"""
		# grab user input from submitted form
		comment_data = request.form['comment']
		comment = Comment(file_name, comment_id, comment_data)
		# apply filter to comment
		comment.apply_filter()
		# propogate changes to db
		db.session.add(comment)
		db.session.commit()
		# re-display the file page.
		return get_file(assignment_name, file_name)

	# return the completed blueprint
	return portfolio_blueprint