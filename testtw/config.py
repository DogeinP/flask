test_db = {
        "user" : "root",
        "password" : "dogun",
        "host" : "localhost",
        "port" : 3306,
        "database" : "testmini"
        }

test_config = {'DB_URL':f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"}
