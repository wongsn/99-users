import tornado.web
import tornado.log
import tornado.options
import sqlite3
import logging
import json
import time
import re
import os 

class App(tornado.web.Application):

    def __init__(self, handlers, **kwargs):
        super().__init__(handlers, **kwargs)

        # Initialising db connection
        self.db = sqlite3.connect("users.db")
        self.db.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cursor = self.db.cursor()

        # Create table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS 'users' ("
            + "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
            + "name TEXT NOT NULL,"
            + "created_at INTEGER NOT NULL,"
            + "updated_at INTEGER NOT NULL"
            + ");"
        )
        self.db.commit()

class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))

# /users
class UsersHandler(BaseHandler): 
    @tornado.gen.coroutine
    def get(self):
        # Parsing pagination params
        page_num = self.get_argument("page_num", 1)
        page_size = self.get_argument("page_size", 10)
        try:
            page_num = int(page_num)
        except:
            logging.exception("Error while parsing page_num: {}".format(page_num))
            self.write_json({"result": False, "errors": "invalid page_num"}, status_code=400)
            return

        try:
            page_size = int(page_size)
        except:
            logging.exception("Error while parsing page_size: {}".format(page_size))
            self.write_json({"result": False, "errors": "invalid page_size"}, status_code=400)
            return

        # Parsing id param
        name = self.get_argument("name", None)
        if name is not None:
            try:
                name = str(name)
            except:
                self.write_json({"result": False, "errors": "invalid id"}, status_code=400)
                return

        # Building select statement
        select_stmt = "SELECT * FROM users"
        # Adding user_id filter clause if param is specified
        if name is not None:
            select_stmt += " WHERE name=?"
        # Order by and pagination
        limit = page_size
        offset = (page_num - 1) * page_size
        select_stmt += " ORDER BY created_at DESC LIMIT ? OFFSET ?"

        # Fetching users from db
        if name is not None:
            args = (name, limit, offset)
        else:
            args = (limit, offset)
        cursor = self.application.db.cursor()
        results = cursor.execute(select_stmt, args)

        users = []
        for row in results:
            fields = ["id", "name", "created_at", "updated_at"]
            user = {
                field: row[field] for field in fields
            }
            users.append(user)

        self.write_json({"result": True, "users": users})

    @tornado.gen.coroutine
    def post(self):
        # Collecting required params
        name = self.get_argument("name")

        # Validating inputs
        errors = []
        name_val = self._validate_name(name, errors)
        time_now = int(time.time() * 1e6) # Converting current time to microseconds

        # End if we have any validation errors
        if len(errors) > 0:
            self.write_json({"result": False, "errors": errors}, status_code=400)
            return

        # Proceed to store the user in our db
        cursor = self.application.db.cursor()
        cursor.execute(
            "INSERT INTO 'users' "
            + "('name','created_at', 'updated_at') "
            + "VALUES (?, ?, ?)",
            (name_val, time_now, time_now)
        )
        self.application.db.commit()

        # Error out if we fail to retrieve the newly created user
        if cursor.lastrowid is None:
            self.write_json(
                {
                    "result": False, 
                    "errors": ["Error while adding user to db"]
                }, 
                    status_code=500)
            return

        user = dict(
            id=cursor.lastrowid,
            name=name_val,
            created_at=time_now,
            updated_at=time_now
        )

        self.write_json({"result": True, "user": user})

    def _validate_name(self, name, errors):
        
        # Generic RegEx matcher for name validation
        # https://stackoverflow.com/questions/61690985/python-regular-expression-to-validate-name-with-one-or-more-words
        match = re.match(r"^[\-'a-zA-Z ]+$", name)
        if match:
            return name
        else:
            logging.exception("Error while parsing: {}".format(name))
            errors.append("invalid name sequence")
            return None
    

# /users/ping
class PingHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.write("pong!")

class UserByIdHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, user_id):
        
        if user_id is not None:
            try:
                user_id = int(user_id)
            except:
                self.write_json({"result": False, "errors": "invalid user_id"}, status_code=400)
                return

        # Building select statement
        select_stmt = "SELECT * FROM users"
        # Adding user_id filter
        if user_id is not None:
            select_stmt += " WHERE id=?"
        # Setting up args
        if user_id is not None:
            args = (user_id,)
        
        # Fetching users from db
        cursor = self.application.db.cursor()
        user_results = cursor.execute(select_stmt, args)
        
        users = []

        for row in user_results:
            fields = ["id", "name", "created_at", "updated_at"]
            user = {
                field: row[field] for field in fields
            }
            users.append(user)
        
        self.write_json({"result": True, "userById": users})


def make_app(options):
    return App([
        (r"/users/ping", PingHandler),
        (r"/users/([^/]+)", UserByIdHandler),
        (r"/users", UsersHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    # Define settings/options for the web app
    # Specify the port number to start the web app on (default value is port 6000)
    tornado.options.define("port", default=6000)
    # Specify whether the app should run in debug mode
    # Debug mode restarts the app automatically on file changes
    tornado.options.define("debug", default=True)

    # Read settings/options from command line
    tornado.options.parse_command_line()

    # Access the settings defined
    options = tornado.options.options

    # Create web app
    app = make_app(options)
    port = int(os.environ.get("PORT", options.port))
    app.listen(port)
    logging.info("Starting user service. PORT: {}, DEBUG: {}".format(port, options.debug))

    # Start event loop
    tornado.ioloop.IOLoop.instance().start()
