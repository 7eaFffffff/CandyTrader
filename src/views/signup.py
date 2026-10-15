import flet as ft
from auth import signup


def signup_view(page: ft.Page):
    username = ft.TextField(label="Username", width=280)

    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=280
    )

    invitation = ft.TextField(
        label="Parent Invitation Code",
        width=280,
        visible=True
    )

    role = ft.Dropdown(
        label="Account Type",
        width=280,
        value="child",
        options=[
            ft.DropdownOption(key="child", text="Child"),
            ft.DropdownOption(key="parent", text="Parent")
        ]
    )

    message = ft.Text(color="red")

    def role_changed(e):
        invitation.visible = role.value == "child"
        page.update()

    role.on_select = role_changed

    def submit(e):
        success, result = signup(
            username.value or "",
            password.value or "",
            role.value,
            invitation.value or ""
        )

        if success:
            page.navigate("/login")
        else:
            message.value = result
            page.update()

    return ft.View(
        route="/signup",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Sign Up", size=36),
                    username,
                    password,
                    role,
                    invitation,
                    message,
                    ft.Button("Create Account", on_click=submit),
                    ft.TextButton(
                        "Already have an account? Log In",
                        on_click=lambda e: page.navigate("/login")
                    )
                ]
            )
        ]
    )
