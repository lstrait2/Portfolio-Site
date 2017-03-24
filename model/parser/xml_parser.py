import xml.etree.ElementTree as ET
from model.portfolio.entries import Directory, File
from model.portfolio.revision import Revision
from model.portfolio.repository import Repository


class XMLParser(object):
	""" Class to allow for Parsing of XML data from subversion
	"""

	def __init__(self, list_file, log_file):
		""" Constructor.

		:param list_file: XML output of svn_list command
		:param log_file: XML output of svn_log command
		"""
		self.svn_repo = None
		self.list_file = list_file
		self.log_file = log_file

	def parse_subversion_xml(self):
		""" Parse XML data from given subversion files

		:return: repository data from given XML files
		"""
		self.svn_repo = self.parse_xml_list()
		self.parse_xml_log()
		return self.svn_repo

	def parse_xml_list(self):
		""" Parse XML output of svn_list command

		:return: repository data from given XML file
		"""
		root = ET.parse(self.list_file).getroot()
		directories = {}
		files = {}
		# grab all entries from list file
		entries = [entry for entry in root.iter('entry')]
		for entry in entries:
			# parse the entry and determine if it is a dictionary or file
			parsed_entry = self.parse_entry(entry)
			if type(parsed_entry) is Directory:
				directories[parsed_entry.name] = parsed_entry
			else:
				files[parsed_entry.name] = parsed_entry
		# return repository data
		return Repository(directories, files)

	def parse_xml_log(self):
		""" Parse XML output of svn_log command

		:return: repository data from given XML file
		"""
		root = ET.parse(self.log_file).getroot()
		log_entries = [log_entry for log_entry in root.iter('logentry')]
		# iterate over each log entry and parse
		for log_entry in log_entries:
			self.parse_log_entry(log_entry)

	def parse_log_entry(self, log_entry):
		""" Parse a single log entry from svn_log file

		:param log_entry: log entry to parse
		"""
		revision_num = log_entry.attrib['revision']
		# iterate over child tags of log entry and parse data
		for child in log_entry.iter():
			if child.tag == 'author':
				author = child.text
			elif child.tag == 'date':
				date = child.text
			elif child.tag == 'msg':
				msg = child.text
		# iterate over all directories and files in path of this entry
		for path in log_entry.iter('path'):
			# remove the shared leading portion of path
			name = path.text[10:]
			# create revision object to store data
			revision = Revision(name, date, author, msg, revision_num)
			entry_obj = None
			# find entry object for this item in path
			if path.attrib['kind'] == 'dir':
					if name in self.svn_repo.directories.keys():
						entry_obj = self.svn_repo.directories[name]
			else:
					if name in self.svn_repo.files.keys():
						entry_obj = self.svn_repo.files[name]
			# add this revision to entry object
			if entry_obj is not None:
				entry_obj.versions.append(revision)

	def parse_entry(self, entry):
		""" Parse individual entry for XML list file

		:param entry: entry to parse
		:return: entry object representing entry
		"""
		# if entry is a directory make Directory object
		if entry.attrib['kind'] == 'dir':
			return self.parse_dir_entry(entry)
		# if entry is a file make File object
		elif entry.attrib['kind'] == 'file':
			return self.parse_file_entry(entry)
		else:
			return None

	def parse_file_entry(self, entry):
		""" create a file object from entry

		:param entry: entry to create file object from
		:return: File object containing data from entry
		"""
		# loop over each child tag and read data
		for child in entry.iter():
			if child.tag == 'name':
				name = child.text
			# last commit in attribute not tag
			elif child.tag == 'commit':
				revision = child.attrib['revision']
			elif child.tag == 'author':
				author = child.text
			elif child.tag == 'date':
				date = child.text
			elif child.tag == 'size':
				size = child.text
		# create object from data
		return File(name, revision, date, author, size)

	def parse_dir_entry(self, entry):
		""" create a directory object from entry

		:param entry: entry to create directory object from
		:return: Directory object containing data from entry
		"""
		# loop over each child tag and read data
		for child in entry.iter():
			if child.tag == 'name':
				name = child.text
			# last commit in attribute not tag
			elif child.tag == 'commit':
				revision = child.attrib['revision']
			elif child.tag == 'author':
				author = child.text
			elif child.tag == 'date':
				date = child.text
		# create object from data
		return Directory(name, revision, date, author)