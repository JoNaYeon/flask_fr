from flask import Flask, render_template

from routes.main_routes import main_bp


def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.register_blueprint(main_bp)

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
