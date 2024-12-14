from flask import Flask

def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Import and register blueprints (if any)
    from .routes import main
    app.register_blueprint(main)

    return app
