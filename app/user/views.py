from __future__ import print_function
import sys

from flask import abort, flash, redirect, render_template, url_for,request,jsonify
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy

from . import user
from .. import db

import pandas as pd
import json
import datetime, decimal

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

@user.route('/userstats')
@login_required
def list_userstats():
    return render_template("user/d3/userstats.html", title='User statistics')

@user.route('/user/charts')
def donorschoose_projects():
    """
    Create data for d3 chart

    A single sql statement is used due to better flexibility of the statement
    """
    db = SQLAlchemy()
    cursor = db.engine.execute("select *,If(winner=%d,1,0) as won,If(winner=%d,0,1) as lost from races where winner = %d or loser = %d and status = 'finished'"
        % (int(current_user.username),int(current_user.username),int(current_user.username),int(current_user.username)) )
    res = cursor.fetchall()

    json_races = json.dumps([dict(r) for r in res], default=alchemyencoder)
    return json_races
