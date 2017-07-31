from __future__ import print_function
import sys




from flask import abort, flash, redirect, render_template, url_for,request,jsonify
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy

from . import admin
from forms import DepartmentForm, EmployeeAssignForm, RoleForm, TrackForm
from .. import db
from ..models import  Track, Trackstats,Daytracks

import pygal

from sklearn.externals import joblib
import pandas as pd
import json
import datetime, decimal



def check_admin():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

# Department Views


@admin.route('/departments', methods=['GET', 'POST'])
@login_required
def list_departments():
    """
    List all departments
    """
    check_admin()

    departments = Department.query.all()

    return render_template('admin/departments/departments.html',
                           departments=departments, title="Departments")


@admin.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    """
    Add a department to the database
    """
    check_admin()

    add_department = True

    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(name=form.name.data,
                                description=form.description.data)
        try:
            # add department to the database
            db.session.add(department)
            db.session.commit()
            flash('You have successfully added a new department.')
        except:
            # in case department name already exists
            db.session.rollback()
            flash('Error: department name already exists.')

        # redirect to departments page
        return redirect(url_for('admin.list_departments'))

    # load department template
    return render_template('admin/departments/department.html', action="Add",
                           add_department=add_department, form=form,
                           title="Add Department")


@admin.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    """
    Edit a department
    """
    check_admin()

    add_department = False

    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the department.')

        # redirect to the departments page
        return redirect(url_for('admin.list_departments'))

    form.description.data = department.description
    form.name.data = department.name
    return render_template('admin/departments/department.html', action="Edit",
                           add_department=add_department, form=form,
                           department=department, title="Edit Department")


@admin.route('/departments/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    """
    Delete a department from the database
    """
    check_admin()

    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('You have successfully deleted the department.')

    # redirect to the departments page
    return redirect(url_for('admin.list_departments'))

    return render_template(title="Delete Department")


# Role Views


@admin.route('/roles')
@login_required
def list_roles():
    check_admin()
    """
    List all roles
    """
    roles = Role.query.all()
    return render_template('admin/roles/roles.html',
                           roles=roles, title='Roles')


@admin.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    """
    Add a role to the database
    """
    check_admin()

    add_role = True

    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                    description=form.description.data)

        try:
            # add role to the database
            db.session.add(role)
            db.session.commit()
            flash('You have successfully added a new role.')
        except:
            # in case role name already exists
            db.session.rollback()
            flash('Error: role name already exists.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    # load role template
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title='Add Role')


@admin.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    """
    Edit a role
    """
    check_admin()

    add_role = False

    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.add(role)
        db.session.commit()
        flash('You have successfully edited the role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    form.description.data = role.description
    form.name.data = role.name
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title="Edit Role")


@admin.route('/roles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_role(id):
    """
    Delete a role from the database
    """
    check_admin()

    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('You have successfully deleted the role.')

    # redirect to the roles page
    return redirect(url_for('admin.list_roles'))

    return render_template(title="Delete Role")


# Employee Views

@admin.route('/employees')
@login_required
def list_employees():
    """
    List all employees
    """
    check_admin()

    employees = Employee.query.all()
    return render_template('admin/employees/employees.html',
                           employees=employees, title='Employees')


@admin.route('/employees/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_employee(id):
    """
    Assign a department and a role to an employee
    """
    check_admin()

    employee = Employee.query.get_or_404(id)

    # prevent admin from being assigned a department or role
    if employee.is_admin:
        abort(403)

    form = EmployeeAssignForm(obj=employee)
    if form.validate_on_submit():
        employee.department = form.department.data
        employee.role = form.role.data
        db.session.add(employee)
        db.session.commit()
        flash('You have successfully assigned a department and role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_employees'))

    return render_template('admin/employees/employee.html',
                           employee=employee, form=form,
                           title='Assign Employee')

@admin.route('/summary')
@login_required
def summary():

    db = SQLAlchemy()

    """
    Plot the results with pygal and render on /latest_results
    """
    #graph = pygal.Line()
    #graph.title = 'Change Coolness'
    cursor = db.engine.execute("SELECT *,victories/(victories+losses) as ratio FROM stats where victories+losses>30")

    return render_template('admin/summary/summary.html', data=cursor.fetchall(), title="summary")

@admin.route('/prob')
@login_required
def prob():

    print('This error output', file=sys.stderr)
    print('Hello world!', file=sys.stderr)
    """
    Plot the results with pygal and render on /latest_results
    """
    #graph = pygal.Line()
    #graph.title = 'Change Coolness'


    return render_template('admin/prob/prob.html',title="probability")

@admin.route('/rfor', methods=['GET', 'POST'])
def rfor():
    clicked=None
    if request.method == "POST":
        clicked=request.json['data']
        challenger=clicked['chall']
        opponent=clicked['oppo']

        #Calculate probs
        clf=joblib.load('app/static/predictive_model/logreg.pkl') #use logistic regression

        #db connection and feature creation
        db = SQLAlchemy()
        cursor = db.engine.execute("SELECT id,victories/(victories+losses) as ratio,victories+losses as total FROM stats ")
        df_stats=pd.DataFrame(cursor.fetchall() ,columns=['id',"ratio","total"])

        df_1 = pd.DataFrame(df_stats[df_stats.id==challenger])
        df_2 = pd.DataFrame(df_stats[df_stats.id==opponent])
        print(df_1)
        if df_1.empty:
            df_1=pd.DataFrame([[0,0,0]],columns=['id',"ratio","total"])
        if df_2.empty:
            print(df_2)
            df_2=pd.DataFrame([[0,0,0]],columns=['id',"ratio","total"])
        X=pd.concat([df_1,df_2]).values
        X=X[:,1:3].flatten()
        print(df_2)
        res=(clf.predict_proba(X))[0].tolist()
        val={}
        val['Lose']=res[0]
        val['Win']=res[1]
    return jsonify(val)

@admin.route('/tracks')
@login_required
def list_tracks():
    """
    List all tracks
    """
    check_admin()

    tracks = Track.query.all()
    print(tracks)
    return render_template('admin/tracks/tracks.html',
                           tracks=tracks, title="Tracks")




@admin.route('/tracks/add', methods=['GET', 'POST'])
@login_required
def add_track():
    """
    Add a department to the database
    """
    check_admin()

    add_track = True

    form = TrackForm()
    if form.validate_on_submit():
        track = Track(name=form.name.data)
        try:
            # add track to the database
            db.session.add(track)
            db.session.commit()
            flash('You have successfully added a new track.')
        except:
            # in case department name already exists
            db.session.rollback()
            flash('Error: track name already exists.')

        # redirect to departments page
        return redirect(url_for('admin.list_tracks'))

    # load department template
    return render_template('admin/tracks/track.html', action="Add",
                           add_track=add_track, form=form,
                           title="Add track")
@admin.route('/tracks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_track(id):
    """
    Edit a department
    """
    check_admin()

    add_track = False

    track = Track.query.get_or_404(id)
    form = TrackForm(obj=track)
    if form.validate_on_submit():
        track.track_id=form.track_id.data
        track.name = form.name.data
        track.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the track.')

        # redirect to the departments page
        return redirect(url_for('admin.list_tracks'))

    form.description.data = track.description
    form.name.data = track.name
    return render_template('admin/tracks/track.html', action="Edit",
                           add_track=add_track, form=form,
                           track=track, title="Edit track")


@admin.route('/trackstats')
@login_required
def list_trackstats():
    return render_template("admin/d3/trackstats.html", title='Track statistics')

@admin.route('/donorschoose/projects')
def donorschoose_projects():
    """
    Create d3 data
    """
    check_admin()

    db = SQLAlchemy()
    #Daytracks=db.query
    cursor = db.engine.execute("select * from day_track_races  ")
    res=cursor.fetchall()

    #day_track_races = Daytracks.query.all()
    #print(day_track_races)
    json_races=json.dumps([dict(r) for r in res], default=alchemyencoder)
    #json.dumps(day_track_races)

    return json_races

    #return render_template('admin/d3/index.html',
    #                       table=races, title="Track statistics")
