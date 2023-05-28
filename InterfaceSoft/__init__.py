import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from InterfaceSoft.local_configs import PRODUCTION, DATABASE_PASSWORD, APP_SECRET_KEY
from InterfaceSoft.app_configs.databases_uri import check_main_db

# create extensions instances
db = SQLAlchemy()  # create a SQLAlchemy object to handle database operations
migrate = Migrate()  # create a Migrate object to handle database migrations


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)  # create a Flask app object with relative instance path
    # app.config.from_object(CustomConfig)
    app.config["SECRET_KEY"] = APP_SECRET_KEY

    def app_data_update():
        # use a try-except block to handle any exceptions
        try:
            # use an if statement to set the database URI for the app
            main_db_uri = check_main_db()
            if main_db_uri:
                app.config["SQLALCHEMY_DATABASE_URI"] = main_db_uri
                print(f"Main database URI: {main_db_uri}")
            else:
                print("No primary node found")
        except Exception as e:
            print(f"An error occurred: {e}")
    app_data_update()

    app.before_request(app_data_update)

    # Set the server name and port of the app
    # app.config["SERVER_NAME"] = SERVER_NAME
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)  # load the config file from the instance folder
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)  # load the test config from the argument

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)  # create the instance folder if it does not exist
    except OSError:
        pass  # ignore the error if it already exists
    # initialize extensions
    db.init_app(app)  # initialize the SQLAlchemy object with the app
    migrate.init_app(app, db)  # initialize the Migrate object with the app and the database

    from . import auth  # import the auth module from the current package
    app.register_blueprint(auth.bp)  # register the auth blueprint with the app

    from . import reading  # import the reading module from the current package
    app.register_blueprint(reading.bp)  # register the reading blueprint with the app
    app.add_url_rule('/', endpoint='index')  # add a URL rule for the index endpoint of the app

    # define error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return 'Page not found', 404  # return a custom message and status code for 404 error

    # from InterfaceSoft.manager.runtime import ManageNetworkDataFlow
    # handle_network_data_flow = ManageNetworkDataFlow()
    # handle_network_data_flow.start()

    return app  # return the app object
