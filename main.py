from app import app
from app.models import FileDetails

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'FileDetails': FileDetails}