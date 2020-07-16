from flask import Flask
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'db.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from public_comment import db
    db.DataManager.init_app(app)

    import public_comment.auth
    app.register_blueprint(auth.bp)

    import public_comment.vox
    app.register_blueprint(vox.bp)

    return app