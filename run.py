import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug='True')

    #app.run(host='0.0.0.0', port=80)


    #app.run(host='162.74.90.100')
