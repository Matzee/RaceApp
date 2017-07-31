#uses the database as classes

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from datetime import datetime

class Employee(UserMixin, db.Model):
    """
    Create an Employee table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Employee: {}>'.format(self.username)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))



class Track(db.Model):
    """
    Create a Track table
    """

    __tablename__ = 'tracks'

    track_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))


    def __repr__(self):
        return '<Track: {}>'.format(self.track_id)


class Daytracks(db.Model):
    """
    Create a Daytracks table
    """

    __tablename__ = 'day_track_races'

    race_driven = db.Column(db.DateTime, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"),primary_key=True)
    cnt_races=db.Column(db.Integer)
    sum_money=db.Column(db.Integer)
    def __repr__(self):
        return "race_driven: %s, track_id: %d    " % (self.race_driven, self.track_id)


class Trackstats(db.Model):
    """
    Create a Track statistics table
    """

    __tablename__ = 'trackstats'

    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"),primary_key=True)
    no_races = db.Column(db.Integer)
    lastrace = db.Column(db.Integer)
    prizemoney = db.Column(db.Integer)
    meanmoney = db.Column(db.Integer)
    minmon = db.Column(db.Integer)
    maxmon = db.Column(db.Integer)
    def __repr__(self):
        return '<Trackstat: {}>'.format(self.track_id)
