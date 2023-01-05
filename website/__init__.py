from flask import Flask, render_template
from datetime import timedelta

def page_not_found(e):
    return render_template("404.html"),404

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "thisismysupersecretkeypleasedonotshareit"
    app.permanent_session_lifetime = timedelta(days=1825)
    app.register_error_handler(404, page_not_found)

    from .views import views
    app.register_blueprint(views,url_prefix="/")

    return app

