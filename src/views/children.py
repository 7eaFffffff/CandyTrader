
import flet as ft
from auth import get_rewards, get_points, get_point_history


def children(page: ft.Page, username: str, on_logout) -> ft.View:

    points_text = ft.Text(
        "0",
        size=42,
        weight=ft.FontWeight.BOLD,
        color="#011638"
    )

    reward_list = ft.Column(spacing=12)
    history_list = ft.Column(spacing=8)

    def refresh_data(e=None):
        # Update current points
        points_text.value = str(get_points(username))

        # Update rewards
        reward_list.controls.clear()

        
        for reward_id, name, cost in get_rewards(username):

            current_points = get_points(username)
            remaining = max(0, cost - current_points)

            if remaining == 0:
                status = "Available to Redeem!"
                status_color = "#2E7D32"
            else:
                status = f"{remaining} more points to redeem"
                status_color = "#777777"

            reward_list.controls.append(
                ft.Container(
                    padding=15,
                    bgcolor="#FFF5CF",
                    border_radius=10,
                    content=ft.Column(
                        spacing=5,
                        controls=[
                            ft.Text(
                                name,
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                f"{cost} Points",
                                size=16
                            ),
                            ft.Text(
                                status,
                                size=12,
                                color=status_color
                            )
                        ]
                    )
                )
            )


        if not reward_list.controls:
            reward_list.controls.append(
                ft.Text("No rewards available yet.")
            )

        # Update point history
        history_list.controls.clear()

        for amount, source, date in get_point_history(username):
            history_list.controls.append(
                ft.Text(f"+{amount} points | {source} | {date}")
            )

        page.update()

    refresh_data()

    return ft.View(
        route="/children",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Text(
                        f"Welcome, {username}",
                        size=28,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        bgcolor="#FFF5CF",
                        border_radius=15,
                        padding=25,
                        width=320,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Current Points", size=20),
                                points_text,
                                ft.Text("pts", size=16)
                            ]
                        )
                    ),

                    ft.Divider(),

                    ft.Text("Reward Shop", size=26),
                    reward_list,

                    ft.Button(
                        "Refresh",
                        on_click=refresh_data
                    ),

                    ft.Divider(),

                    ft.Text("Point History", size=24),
                    history_list,
                    ft.Divider(),
                    ft.Button(
                        "Log Out",
                        on_click=on_logout
                    )
                ]
            )
        ]
    )
