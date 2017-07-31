# RaceApp

Flask App for the Big Data Coding Competition (it-talents)
* Data Visualisation with DC,D3 and Crossfilter
* Python 2.7 is used
* Used packages can be found in requirements.txt
* Predictive Model is built and tuned in advance with sklearn. Random Forest is compared with logistic Regression. Logistic Regression is chosen in final. Predictive Model is dumped in a file and loaded each time when it is used.
* Analogous to a Data Warehouse with OLAP functionalities, sql queries are saved as new tables to reduce calculation time --> Break of ACID philosopy

## Principal information
* There are two possible Login Roles.
  * Admin-Role:
    * Login: admin@admin.com
    * Password: admin2016
  * User-Role:
    * Login: 1@user.com
    * Password: 123456

## Installation

1) Be sure to have mysql installed

2) Use following codes in Bash/Terminal

    git clone

    mysql < schema.sql

    pip install -r requirements.txt

    export FLASK_CONFIG=development

    export FLASK_APP=run.py

    flask run

## Further improvements

* Use Docker (Docker-Compose) for easier installation and use
* Create single executable
* Adding races
  * Therefor building stored procedures in mysql for the calculated tables
