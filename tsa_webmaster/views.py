from flask import render_template, Blueprint, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from tsa_webmaster import db
from tsa_webmaster.models import Resources, User, ResourceAttendees
from tsa_webmaster.forms import ResourceForm, RegisterForm, LoginForm
from sqlalchemy import select
from datetime import datetime, timezone

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@views.route('/from<string:indexmessage>', methods=['GET', 'POST'])
def index(page = 1, indexmessage = "None"):
    resources = db.paginate(select(Resources).order_by(Resources.created_date.desc()), page=1, per_page=9)
    return render_template('index.html', resources=resources, indexmessage=indexmessage)

@views.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('views.login', loginmessage = "register"))
    return render_template('register.html', form=form)

@views.route('/login', methods=['GET', 'POST'])
@views.route('/login/<string:loginmessage>', methods=['GET', 'POST'])
def login(loginmessage = "None"):
    
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(select(User).filter_by(email=form.email.data)).scalar_one_or_none()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('views.index', indexmessage = "login"))
        else:
            return render_template('login.html', form=form, loginmessage = 'invalid')
    return render_template('login.html', form=form, loginmessage=loginmessage)

@login_required
@views.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.index', indexmessage = 'logout'))

@login_required
@views.route('/submit-resource', methods=['GET', 'POST'])
def submit_resource():
    if current_user.is_authenticated:
        form = ResourceForm()

        if form.validate_on_submit():
            if form.resource_category.data == 'volunteering':
                resource_category = 'Volunteering'
                resource_tags = ", ".join(form.resource_volunteering_tags.data)
            elif form.resource_category.data == 'education':
                resource_category = 'Education'
                resource_tags = ", ".join(form.resource_education_tags.data)
            elif form.resource_category.data == 'recreation':
                resource_category = 'Recreation'
                resource_tags = ", ".join(form.resource_recreation_tags.data)
            else:
                resource_category = 'Miscellaneous'
                resource_tags = "None"
            resource = Resources(
                created_date=datetime.now(timezone.utc),
                user_id=current_user.id,
                resource_title=form.resource_title.data,
                resource_description=form.resource_description.data,
                resource_date = form.resource_date.data,
                resource_time=form.resource_time.data,
                resource_location=form.resource_location.data, 
                resource_category=resource_category,
                resource_tags=resource_tags)

            db.session.add(resource)
            db.session.commit()
            return redirect(url_for('views.index', indexmessage = "submit"))

        return render_template('submit.html', form=form)

    else:
        return redirect(url_for('views.login', loginmessage = "submit"))


@views.route('/resource/<int:resource_id>')
@views.route('/resource/<int:resource_id>/<string:resourcemessage>', methods=['GET', 'POST'])
def resource(resource_id, resourcemessage = "None"):
    resource = db.session.execute(select(Resources).filter_by(id = resource_id)).scalar_one_or_none()
    if resource:
        if resource.attendees and db.session.execute(select(ResourceAttendees).filter_by(resource_id = resource_id, user_id = current_user.id)).scalar_one_or_none():
            is_attending = True
        else:
            is_attending = False

        return render_template('resource.html', resource=resource, resourcemessage=resourcemessage, is_attending=is_attending)
    else:
        return redirect(url_for('views.index', indexmessage = 'resource'))

@login_required
@views.route('/account/<int:current_user_id>')
def account(current_user_id):
    user = db.session.execute(select(User).filter_by(id=current_user_id)).scalar_one_or_none()
    if user:
        return render_template('account.html', user=user)
    else:
        return redirect(url_for('views.index', indexmessage = 'account'))

@views.route('/about')
def about():
    return render_template('about.html')

@login_required
@views.route('/delete/<int:resource_id>')
def delete(resource_id):
    resource = db.session.execute(select(Resources).filter_by(id = resource_id)).scalar_one_or_none()
    if resource and resource.user_id == current_user.id:
        db.session.delete(resource)
        db.session.commit()
        return redirect(url_for('views.index', indexmessage = 'delete'))
    else:
        return redirect(url_for('views.resource', resource_id=resource_id, resourcemessage = 'delete'))

@login_required
@views.route('/attend/<int:resource_id>')
def attend(resource_id):
    if current_user.is_authenticated:
        resource = db.session.scalar(select(Resources).filter_by(id = resource_id))
        if resource:
            if resource.user_id != current_user.id:
                if current_user.id not in resource.attendees:
                    db.session.add(ResourceAttendees(resource_id = resource_id, user_id = current_user.id))
                    db.session.commit()
                    return redirect(url_for('views.resource', resource_id = resource_id, resourcemessage = 'attend'))
                else:
                    return redirect(url_for('views.resource', resource_id = resource_id, resourcemessage = 'already_attending'))
            else:
                return redirect(url_for('views.resource', resource_id = resource_id, resourcemessage = 'already_created'))
        else:
            return redirect(url_for('views.index', resource_id = resource_id, indexmessage = 'resource'))
    else:
        return redirect(url_for('views.login', loginmessage = 'attend'))

@login_required
@views.route('/unattend/<int:resource_id>')
def unattend(resource_id):
    if current_user.is_authenticated:
        resource = db.session.scalar(select(Resources).filter_by(id = resource_id))
        if resource:
            if resource.user_id != current_user.id:
                user = db.session.scalar(select(ResourceAttendees).filter_by(resource_id = resource_id, user_id = current_user.id))
                if user:
                    db.session.delete(user)
                    db.session.commit()
                    return redirect(url_for('views.resource', resource_id = resource_id, resourcemessage = 'unattend'))
                else:
                    return redirect(url_for('views.resource', resource_id = resource_id, resourcemessage = 'not_attending'))
            else:
                return redirect(url_for('views.resource', resource_id = resource_id, resourcemessage = 'already_created'))
        else:
            return redirect(url_for('views.index', indexmessage = 'resource'))
    else:
        return redirect(url_for('views.login', loginmessage = 'unattend'))