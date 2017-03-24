from app import app, db
from model.portfolio.repository import Repository
from view.portfolio_views import construct_portfolio_blueprint

# create portfolio using database
portfolio = Repository.generate_portfolio_from_db(db)
# register routes for portfolio
app.register_blueprint(construct_portfolio_blueprint(portfolio))
if __name__ == '__main__':
	# run the app
	app.run()