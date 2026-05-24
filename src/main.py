import flet as ft
import searching
import database


def main(page: ft.Page):
    searchbar = ft.TextField(label="Your Goal", hint_text="What you want to learn")
    searchService = ft.Row([searchbar,
                            ft.Button("Search", on_click=lambda e: searching.searcher(page, searchbar.value, database.test))])

    '''page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click= searching.searcher(page, searchbar.value, database.test) 
    )'''
    '''ft.SafeArea(
            expand=True,
            content=ft.Container(
                content=searchService,
                alignment=ft.Alignment.CENTER,
            ),
        )'''

    page.add(
        
        searchService
    )


ft.run(main)
