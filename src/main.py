"""Mentor — knowledge prerequisite explorer."""

import flet as ft


import exporting
import searching


@ft.control
class Mentor(ft.Container):
    bgcolor: str = "#F2DEA4"
    width: int = 600
    padding: int = 20

    def init(self):
        self.databasepath = None
        self.engine_mode = "dict"

        self.database_field = ft.TextField(
            label="Choose one database",
            hint_text="The address of your database. Left Blank will use intrinsic database. " \
            "Please press Enter after you type in the path",
            bgcolor="#A3B1F2",
            expand=True,
            autofocus=True,
            on_submit=self._choose_database,
        )

        self.engine_selector = ft.Dropdown(
            value="dict",
            options=[
                ft.dropdown.Option("dict", "Dict (substring)"),
                ft.dropdown.Option("vespa", "Vespa (BM25)"),
            ],
            on_select=self._on_engine_change,
            tooltip="Search engine backend",
            expand=True,
        )

        self.search_field = ft.TextField(
            label="Your Goal",
            hint_text="What you want to learn",
            bgcolor="#A3B1F2",
            expand=True,
            autofocus=True,
            on_submit=self._on_search,
        )
        self.search_btn = ft.IconButton(
            icon=ft.Icons.SEARCH,
            tooltip="Search prerequisites",
            on_click=self._on_search,
        )

        self.export_mode = "None"
        self.exportAddress_field = ft.TextField(
            hint_text="path/to/output.md",
            expand=True,
            bgcolor="#A3B1F2",
        )
        self.setExportMode_btn = ft.Dropdown(
            value="None",
            options=[
                ft.dropdown.Option(key=mode, text=mode)
                for mode in exporting.EXPORT_MODES
            ],
            on_select=self.changeExportMode,
        )

     
        self.result_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        self.content = ft.Column(
            controls=[
                ft.Row([self.database_field]),
                ft.Row([self.engine_selector]),
                ft.Row([self.search_field, self.search_btn]),
                ft.Row([self.setExportMode_btn, self.exportAddress_field]),
                ft.Divider(),
                self.result_list,
            ],
            expand=True,
        )

    def _on_search(self, e) -> None:
        query = self.search_field.value.strip()

        self.result_list.controls.clear()

        if not query:
            self.result_list.controls.append(
                ft.Text("Enter a topic to search.", italic=True, color="#888888"),
            )
            self.update()
            return

        matches = searching.search(query, base=self.databasepath, engine=self.engine_mode)

        if not matches:
            self.result_list.controls.append(
                ft.Text(
                    f'No match for "{query}". Try another keyword or database.',
                    color="#CC4444",
                ),
            )
            self.update()
            return

        chains_db: dict[str, list[tuple[int, str]]] = {}

        for topic in matches:
            self.result_list.controls.append(
                ft.Text(f"📚 {topic}", size=18, weight=ft.FontWeight.BOLD),
            )

            chain = searching.prerequisite_chain(
                topic,
                base=self.databasepath,
                max_depth=3,
            )
            chains_db[topic] = chain

            if not chain:
                self.result_list.controls.append(
                    ft.Text(
                        "  (no known prerequisites)",
                        italic=True,
                        color="#666666",
                    ),
                )
            else:
                for depth, prereq in chain:
                    marker = "#" * depth
                    self.result_list.controls.append(
                        ft.Text(f"{marker}{prereq}"),
                    )

        self.update()

        export_path = self.exportAddress_field.value.strip()
        if self.export_mode != "None":
            if not export_path:
                self.result_list.controls.append(
                    ft.Text(
                        "Export is enabled but no file path is set.",
                        color="#CC4444",
                    ),
                )
                self.update()
            else:
                try:
                    content = exporting.to_markdown(
                        query, matches, chains_db,
                    )
                    exporting.write_file(export_path, content)
                except OSError:
                    self.result_list.controls.append(
                        ft.Text(
                            f'Failed to write to "{export_path}".',
                            color="#CC4444",
                        ),
                    )
                    self.update()

    def _choose_database(self, e) -> None:
        self.databasepath = self.database_field.value.strip()

    def changeExportMode(self, e) -> None:
        self.export_mode = self.setExportMode_btn.value

    def _on_engine_change(self, e) -> None:
        self.engine_mode = self.engine_selector.value


def main(page: ft.Page):
    page.title = "Mentor"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    page.add(Mentor())


ft.run(main)
