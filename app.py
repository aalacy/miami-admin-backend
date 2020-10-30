from app import create_app, db, cli

app = create_app()
app.app_context().push()
cli.register(app)

