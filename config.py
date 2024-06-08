class Config:
    db_type = 'postgresql'
    username = 'postgres'
    password = 'admin'
    host = 'localhost'
    database_name = 'school'

    SQLALCHEMY_DATABASE_URI = f'{db_type}://{username}:{password}@{host}/{database_name}'


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your_secret_key_here"  #TODO Generate a strong secret key
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 90

    IMAGE_UPLOAD_DIR = "uploaded/img"
    FILES_UPLOAD_DIR = "uploaded/teachers"
    BOARD_SAVE_DIR = "uploaded/boards"
