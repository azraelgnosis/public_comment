from flask import Flask
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'db.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    import public_comment.auth
    app.register_blueprint(auth.bp)

    import public_comment.um
    app.register_blueprint(um.bp)

    return app