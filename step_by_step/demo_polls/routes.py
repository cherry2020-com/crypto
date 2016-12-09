import pathlib

from views import hello

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/hello/{name:\w*}', hello, name="hello")
    app.router.add_static('/static/',
                          path=str(PROJECT_ROOT / 'static'),
                          name='static', show_index=True, follow_symlinks=True)
