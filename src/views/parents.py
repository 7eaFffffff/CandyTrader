
import flet as ft
from auth import generate_invite, get_children, add_reward


def parents(page: ft.Page, username: str, on_logout):
    code_text = ft.Text("", size=18, selectable=True)
    children_column = ft.Column()

    reward_name = ft.TextField(
        label="Reward Name",
        hint_text="e.g. Ice Cream",
        width=280
    )

    reward_points = ft.TextField(
        label="Point Cost",
        hint_text="e.g. 50",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=280
    )

    reward_message = ft.Text("")

    def refresh_children():
        children_column.controls.clear()
        for child in get_children(username):
            children_column.controls.append(
                ft.Text(f"Child: {child}")
            )
        page.update()

    def create_code(e):
        code = generate_invite(username)
        if code:
            code_text.value = f"Invitation code: {code}"
        else:
            code_text.value = "Unable to generate code"
        page.update()

    def create_reward(e):
        success, message = add_reward(
            username,
            reward_name.value or "",
            reward_points.value or ""
        )

        reward_message.value = message

        if success:
            reward_name.value = ""
            reward_points.value = ""

        page.update()

    # Initial children list
    for child in get_children(username):
        children_column.controls.append(
            ft.Text(f"Child: {child}")
        )

    return ft.View(
        route="/parents",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Text(
                        f"Welcome, {username}",
                        size=30,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text("Invitation Codes", size=22),
                    ft.Button(
                        "Generate Invitation Code",
                        on_click=create_code
                    ),
                    code_text,

                    ft.Divider(),

                    ft.Text("My Children", size=22),
                    children_column,
                    ft.Button(
                        "Refresh Children",
                        on_click=lambda e: refresh_children()
                    ),

                    ft.Divider(),

                    ft.Text("Add a Reward", size=24),
                    reward_name,
                    reward_points,
                    ft.Button(
                        "Add Reward",
                        on_click=create_reward
                    ),
                    reward_message,

                    ft.Divider(),

                    ft.Button("Log Out", on_click=on_logout)
                ]
            )
        ]
    )
