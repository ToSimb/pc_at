from database.database import Database
from fastapi import Depends, Request

def get_db_pool(request: Request):
    return request.app.state.pool

def get_db_repo(conn = Depends(get_db_pool)):
    return Database(conn)