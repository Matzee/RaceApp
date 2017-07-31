# RaceApp

Flask App for the Big Data Coding Competition (IT-talents)
* Python 2.7 is used
* Used packages can be found in requirements.txt
* Predictive Model is built and tuned in advance with sklearn. Random Forest is compared with logistic Regression. Logistic Regression is chosen in final. Predictive Model is dumped.

## Principal information
* There are two possible Login Roles.
  * Admin-Role:
    * Login: admin@admin.com
    * Password: admin2016
  * User-Role:
    * Login: 1@user.com
    * Password: 123456

## Installation

* git clone
* Download mysql
* source schema.sql
* pip install -r requirements.txt
* export FLASK_CONFIG=development
* export FLASK_APP=run.py
* flask run
