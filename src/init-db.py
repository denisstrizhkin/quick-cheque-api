from api import init_db, app

with app.app_context():
    init_db()
