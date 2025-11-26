import traceback
try:
    import app
    print('app module file:', getattr(app, '__file__', None))
    print('app.create_app:', app.create_app)
    print('callable:', callable(app.create_app))
    import inspect
    try:
        print('\n--- create_app source ---')
        print(inspect.getsource(app.create_app))
        print('--- end source ---\n')
    except Exception as e:
        print('Could not retrieve source:', e)
    a = app.create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "SQLALCHEMY_TRACK_MODIFICATIONS": False})
    print('returned:', a)
    if a is not None:
        print('has app_context attr:', hasattr(a, 'app_context'))
        print('config keys sample:', list(a.config.keys())[:5])
except Exception:
    traceback.print_exc()
