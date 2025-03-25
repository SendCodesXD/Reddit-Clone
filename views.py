import aiohttp

import flet as ft

from utils import parse_reddit_data
from conf import BASE_API_URL, BASE_AUTH_URL


class LoginView:
    def __init__(self, page: ft.Page, login_handler):
        self.page = page
        self.login_handler = login_handler


    @property
    def header_view(self):
        header_text = ft.Container(
                    content=ft.Text("CS12 Project"),
                    alignment=ft.alignment.center,
                    width=100,
                    height=50,
                )
        header_bar_row = ft.Row(
            width=self.page.window_max_width,
            controls=[
                ft.Container(
                    expand=1,
                    content=ft.Row([header_text], alignment=ft.MainAxisAlignment.START),
                    bgcolor=ft.colors.GREY_100,
                ),
            ]
        )
        return header_bar_row


    @property
    def login_view(self):
        auth_url_input = ft.Container(content=ft.TextField(label="BASE AUTH URL", value=BASE_AUTH_URL))
        api_url_input = ft.Container(content=ft.TextField(label="BASE API URL", value=BASE_API_URL))
        login_button = ft.Container(content=ft.ElevatedButton("Login", on_click=self.login_handler))
        login_row = ft.Row(
            width = self.page.window_max_width,
            controls=[
                ft.Container(
                    expand=1,
                    content=ft.Column([auth_url_input, api_url_input, login_button], spacing=10)
                )
            ]
        )
        return login_row
    
    async def setup(self):
        await self.page.clean_async()
        await self.page.add_async(self.header_view, self.login_view)
    

class DashBoardView:
    def __init__(self, page: ft.Page, logout_handler, refresh_handler, load_more_handler):
        self.page = page
        self.logout_handler = logout_handler
        self.refresh_handler = refresh_handler
        self.load_more_handler = load_more_handler
        self.posts_data = []
        self.after = None
    
    @property
    def header_bar(self):
        refresh_text = ft.Container(
            content=ft.Icon(ft.icons.REFRESH_ROUNDED),
            on_click=self.refresh_handler
        )
        logout_text = ft.Container(
                    content=ft.Text("Logout"),
                    alignment=ft.alignment.center,
                    width=100,
                    height=50,
                    on_click=self.logout_handler
                )
        left_container = ft.Container(
            content=ft.Row([refresh_text, logout_text], spacing=10)
        )
        header_text = ft.Container(
                    content=ft.Text("Home"),
                    alignment=ft.alignment.center,
                    width=100,
                    height=50,
                )
        header_bar = ft.Row(
                    width=self.page.window_max_width,
                    controls=[
                        ft.Container(
                            expand=1,
                            content=ft.Row([header_text, left_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            bgcolor=ft.colors.GREY_100,
                            
                        ),
                    ]
        )

        return header_bar
    
    def get_posts_list_view(self, post):
        upvote_color = ft.colors.ORANGE if post['likes'] else ft.colors.GREY
        downvote_color = ft.colors.BLUE if post['likes'] is False else ft.colors.GREY
        count = ft.Container(
            content=ft.Text(post['score'],
                            text_align=ft.TextAlign.CENTER,
                            ),
                        
            )
        upvote_container = ft.Container(
            content=ft.Icon(ft.icons.ARROW_UPWARD, color=upvote_color),
        )
        downvote_container = ft.Container(
            content=ft.Icon(ft.icons.ARROW_DOWNWARD, color=downvote_color),
        )
        first_part = ft.Column(
            spacing=20,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[upvote_container, count, downvote_container],
        )
        title_container = ft.Container(
            content=ft.Text(post['title']),
        )

        post_comments = ft.Container(
            content=ft.Text(f"{post['num_comments']} comments"),
        )

        post_author = ft.Container(
            content=ft.Text(post['author']),
        )

        post_subreddit = ft.Container(
            content=ft.Text(post['subreddit']),
        )

        post_combined_meta = ft.Row(
            spacing=20,
            controls=[post_comments, post_author, post_subreddit]
        )

        second_part = ft.Column(
            spacing=5,
            controls=[title_container, post_combined_meta]
        )
        
        final_post_view = ft.Container(
            padding=30,
            content=ft.Row(
                width=self.page.window_max_width,
                spacing=30,
                controls=[first_part, second_part]
            ),
            bgcolor="#F0F4FA",
            border=ft.border_radius.all(20)
        )
        
        return final_post_view

    @property
    def posts_list(self):
        post_lists = ft.ListView(spacing=10, padding=20, height=800)
        for post in self.posts_data:
            final_post_view = self.get_posts_list_view(post)
            post_lists.controls.append(final_post_view)
        post_lists.controls.append(self.load_more)
        self._post_list_control = post_lists
        return post_lists


    @property
    def load_more(self):
        load_more_text = ft.Container(content=ft.Text("Load More", size=20), on_click=self.load_more_handler)
        load_more = ft.Container(
            content=ft.Row(
                width=self.page.window_max_width,
                spacing=30,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[load_more_text]
            ),
            bgcolor="#F0F4FA",
            border=ft.border_radius.all(20)

        )
        return load_more

    async def get_posts_data(self, next_page=False):
        headers = {
            'Authorization': f'Bearer {self.page.auth.token.access_token}'
        }

        url = f'{BASE_API_URL}/new.json'
        
        if next_page and self.after:
            url = f'{url}?after={self.after}'

        request = aiohttp.request(
            method='GET',
            url=url,
            headers=headers,
        )
        async with request as response:
            data = await response.json()
            return data
    
    async def load_posts_data(self):
        data = await self.get_posts_data()
        if data:
            after, posts = parse_reddit_data(data)
            self.posts_data = posts
            self.after = after

    async def setup(self):
        await self.page.clean_async()
        await self.page.add_async(self.header_bar, self.posts_list)
    
    async def remove_posts_lists(self):
        await self.page.remove_async(self._post_list_control)
    
    async def add_posts_lists(self):
        await self.load_posts_data()
        await self.page.add_async(self.posts_list)

    async def load_more_posts(self):
        next_data = await self.get_posts_data(next_page=True)
        if next_data:
            after, posts = parse_reddit_data(next_data)
            self.after = after
        
            post_lists = self._post_list_control
            post_lists.controls.pop()

            for post in posts:
                final_post_view = self.get_posts_list_view(post)
                post_lists.controls.append(final_post_view)
            
            post_lists.controls.append(self.load_more)
            await self.page.update_async(post_lists)
    