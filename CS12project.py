import logging
import base64
import flet as ft
from flet.version import version
from flet.auth.oauth_provider import OAuthProvider
from flet.auth.authorization import Authorization


from views import LoginView, DashBoardView
from conf import CLIENT_ID, CLIENT_SECRET, BASE_AUTH_URL, REDIRECT_URL, PORT_NO

logging.basicConfig(level=logging.INFO)
logging.getLogger("flet_core").setLevel(logging.INFO)


class MyAuthorization(Authorization):
    def __init__(self, *args, **kwargs):
        super(MyAuthorization, self).__init__(*args, **kwargs)

    def _Authorization__get_default_headers(self):
        encoded = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf8')).decode('utf8')
        return {"User-Agent": f"Flet/{version}", "Authorization": f"Basic {encoded}"} 


async def main(page: ft.Page):
    provider = OAuthProvider(
        client_id=CLIENT_ID,
        client_secret="",
        authorization_endpoint=f'{BASE_AUTH_URL}/api/v1/authorize.compact?duration=permanent',
        token_endpoint=f'{BASE_AUTH_URL}/api/v1/access_token',
        redirect_url=REDIRECT_URL,
        user_scopes=['identity', 'read']
    )   

    async def login_reddit(e):
        await page.login_async(provider, authorization=MyAuthorization)


    async def logout_reddit(e):
        await page.logout_async()

    async def on_logout(e):
        await login_view.setup()

    async def on_login(e):
        if not e.error:
            await dashboard_view.load_posts_data()
            await dashboard_view.setup()
        else:
            logging.info(f"Error: {e.error}")
    
    async def refresh_posts(e):
        await dashboard_view.remove_posts_lists()
        await dashboard_view.add_posts_lists()
    

    async def load_more_posts(e):
        await dashboard_view.load_more_posts()

    login_view = LoginView(page, login_reddit)
    dashboard_view = DashBoardView(page, logout_reddit, refresh_posts, load_more_posts)
    page.on_login = on_login
    page.on_logout = on_logout
    await login_view.setup()

ft.app(target=main, port=PORT_NO, view=ft.WEB_BROWSER)
