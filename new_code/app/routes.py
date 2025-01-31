from flask import render_template, flash, redirect, request,url_for
from app import app,db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from encrypt_file import encrypt_and_save_file
from flask import current_app
from werkzeug.utils import secure_filename

def validateExtension(filename):
	print("in validate extension")
	return '.' in filename and filename.split('.')[-1] in current_app.config.get('ALLOWED_EXTENSIONS')

def validateAndGetFileSize(file):
	chunk = 16 #chunk size to read per loop iteration; 16 bytes
	data = None
	size = 0
	#keep reading until out of data
	print("in validate file size")
	while data != b'':
		data = file.read(chunk)
		print("val data=",data)
		size += len(data)
		#return false if the total size of data parsed so far exceeds MAX_FILE_SIZE
		if size > current_app.config.get('MAX_FILE_SIZE'):
			return 0
	return size

@app.route('/')
@app.route('/index')
@login_required
def index():
	return render_template('index.html',title='Home')

@app.route('/login', methods = ['GET','POST'])
def login():
	print("In login")
	if current_user.is_authenticated:
		return redirect(url_for('index'))	
	form = LoginForm()
	if form.validate_on_submit():
		print("Inside if")
		user = User.query.filter_by(username = form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember = form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register',methods = ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username = form.username.data, email = form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html',title = 'Register', form = form)

@app.route('/upload',methods = ['GET'])
@login_required
def upload():
	return render_template('file_upload.html',title='Upload File',form = None)


@app.route('/handle_upload',methods=['POST'])
@login_required
def handle_upload():

	print("Posted file: {}".format(request.files['file']))
	secret = current_user.get_password_hash()
	print(secret)
	file = request.files['file']
	file_size = validateAndGetFileSize(file)
	if file and file_size and validateExtension(secure_filename(file.filename)):
		encrypt_and_save_file(secret,file,file_size)
	return "File uploaded"