import configparser
import os

class ConfigError(Exception):
    pass

def load_config(path="config.ini"):
    if not os.path.isfile(path):
        raise ConfigError(f"Config file '{path}' not found.")

    config = configparser.ConfigParser()
    config.read(path)

    if "database" not in config:
        raise ConfigError("Missing [database] section in config file.")

    db = config["database"]

    required = ["user", "password", "host", "port", "service", "encoding"]
    for field in required:
        if field not in db or not db[field].strip():
            raise ConfigError(f"Missing or empty '{field}' in config file.")

    try:
        port = int(db["port"])
        if port <= 0 or port > 65535:
            raise ValueError
    except ValueError:
        raise ConfigError("Port must be a positive integer.")

    dsn = f"{db['host']}:{port}/{db['service']}"

    return {
        "user": db["user"],
        "password": db["password"],
        "dsn": dsn,
        "encoding": db["encoding"]
    }

def load_paths(path="config.ini"):
    if not os.path.isfile(path):
        raise ConfigError(f"Config file '{path}' not found.")

    config = configparser.ConfigParser()
    config.read(path)

    if "path" not in config:
        raise ConfigError("Missing [path] section in config file.")

    paths = config["path"]
    required = ["db_code" ,"import_account", "import_customer", "import_service", "import_hall"]
    for field in required:
        if field not in paths or not paths[field].strip():
            raise ConfigError(f"Missing or empty '{field}' in config file.")

    for path in paths.values():
        if not os.path.isfile(path):
            raise ConfigError(f"Path '{path}' does not exist.")

    return {
        "db_code": paths["db_code"],
        "import_account": paths["import_account"],
        "import_customer": paths["import_customer"],
        "import_service": paths["import_service"],
        "import_hall": paths["import_hall"]
    }