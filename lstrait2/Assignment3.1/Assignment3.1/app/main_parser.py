from app import db
from model.parser.xml_parser import XMLParser
from model.portfolio.entries import Directory, File
from model.portfolio.revision import Revision
from model.filter import Filter

if __name__ == '__main__':
	# create tables if they do not exist
	db.create_all()
	# run the parser to collect data
	portfolio = XMLParser('resources/data/svn_list_new.xml', 'resources/data/svn_log_new.xml').parse_subversion_xml()

	# add new data to portfolio
	for directory in portfolio.directories.values():
		# if directory not in database, add it
		if not Directory.query.filter_by(name=directory.name).first():
			db.session.add(directory)
			db.session.commit()
		# otherwise update the existing entry
		else:
			# must update each attribute manually bc of SQLAlchemy limitations
			directory_row = Directory.query.filter_by(name=directory.name).first()
			directory_row.name = directory.name
			directory_row.revision = directory.revision
			directory_row.date = directory.date
			directory_row.summary = directory.summary
			directory_row.author = directory.author
			directory_row.parent_name = directory.parent_name
		for version in directory.versions:
			if Revision.query.filter_by(name=version.name, revision=version.revision):
				db.session.add(version)
				db.session.commit()
			# no need for else clause here since old revision will not be updated
	for file in portfolio.files.values():
		# if file not in database, add it
		if not File.query.filter_by(name=file.name).first():
			db.session.add(file)
			db.session.commit()
		# otherwise update existing entry
		else:
			# must update each attribute manually bc of SQLAlchemy limitations
			file_row = File.query.filter_by(name=file.name).first()
			file_row.name = file.name
			file_row.revision = file.revision
			file_row.date = file.date
			file_row.summary = file.summary
			file_row.author = file.author
			file_row.parent_name = file.parent_name
		for version in file.versions:
			if not Revision.query.filter_by(name=version.name, revision=version.revision).first():
				db.session.add(version)
				db.session.commit()
			# no need for else clause here since old revision will not be updated

	# add 5 filtered words to database
	filtered_words = [Filter("shit", "apple"), Filter("fuck", "banana"), Filter("ass", "lemon"),
					  Filter("bitch", "pineapple"), Filter("damn", "grape")]
	for filtered_word in filtered_words:
		if not Filter.query.filter_by(word=filtered_word.word).first():
			db.session.add(filtered_word)
			db.session.commit()