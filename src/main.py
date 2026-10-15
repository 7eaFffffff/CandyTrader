
import flet as ft
from auth import init_db
from views.login import login_view
from views.signup import signup_view
from views.children import children
from views.parents import parents

def main(page: ft.Page):
    init_db()

    page.title = "User Profile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed="#fff5cf")
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = False
    Button_Width=200
    Button_Height=50

    current_user = None
    current_role = None

    def on_success(username, role):
        nonlocal current_user, current_role
        current_user = username
        current_role = role

    def logout(e):
        nonlocal current_user, current_role
        current_user = None
        current_role = None
        page.navigate("/login")

    def home_view():
        return ft.View(
            route="/",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Choose your role", size=36),
                        ft.Button(
                            "Log In",
                            on_click=lambda e: page.navigate("/login"),width=Button_Width,height=Button_Height
                        ),
                        ft.Button(
                            "Sign Up",
                            on_click=lambda e: page.navigate("/signup"),width=Button_Width,height=Button_Height
                        )
                    ]
                )
            ]
        )

    def route_change(e=None):
        print("ROUTE:", page.route)
        print("USER:", current_user)
        print("ROLE:", current_role)

        page.views.clear()
        page.views.append(home_view())

        if page.route == "/login":
            page.views.append(login_view(page, on_success))

        elif page.route == "/signup":
            page.views.append(signup_view(page))

        elif page.route == "/parents":
            print("PARENT PAGE REQUESTED")

            if current_user is None or current_role != "parent":
                print("ACCESS DENIED")
                page.navigate("/login")
                return

            print("LOADING PARENT VIEW")
            page.views.append(parents(page, current_user, logout))

        elif page.route == "/children":
            if current_user is None or current_role != "child":
                page.navigate("/login")
                return

            page.views.append(children(page, current_user, logout))

        page.update()

    page.on_route_change = route_change
    route_change()

if __name__ == "__main__":
    ft.run(main)
