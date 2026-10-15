import flet as ft
from auth import login

def login_view(page: ft.Page, on_success):
    username = ft.TextField(
        label="Username",
        width=280
    )

    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=280
    )

    message = ft.Text(color="red")

    def submit(e):
        role = login(username.value, password.value)

        if role is None:
            message.value = "Invalid username or password"
            page.update()
        else:
            on_success(username.value.strip(), role)
            page.navigate("/children" if role == "child" else "/parents")

    return ft.View(
        route="/login",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Log In", size=36, weight=ft.FontWeight.BOLD),
                    username,
                    password,
                    message,
                    ft.Button("Log In", on_click=submit),
                    ft.TextButton(
                        "Create an Account",
                        on_click=lambda e: page.navigate("/signup")
                    )
                ]
            )
        ]
    )
