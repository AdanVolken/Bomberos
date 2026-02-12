import flet as ft
import hashlib
from database import get_connection, obtener_maquinas_licencia, eliminar_maquina_licencia

def mostrar_admin_cuentas(page: ft.Page):

    def refrescar_lista():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, cliente, max_maquinas FROM licencia")
        usuarios = cursor.fetchall()
        conn.close()

        lista.controls.clear()

        for u in usuarios:
            licencia_id = u["id"]
            cliente = u["cliente"]
            max_maquinas = u["max_maquinas"]

            nuevo_cupo = ft.TextField(
                label="Máx. máquinas",
                value=str(max_maquinas),
                width=130,
                bgcolor=ft.Colors.GREY_700,
                color=ft.Colors.WHITE,
                label_style=ft.TextStyle(color=ft.Colors.WHITE70),
                border_color=ft.Colors.GREY_600,
                focused_border_color=ft.Colors.BLUE_400,
                keyboard_type=ft.KeyboardType.NUMBER
            )

            nueva_pass = ft.TextField(
                label="Nueva contraseña",
                password=True,
                width=200,
                bgcolor=ft.Colors.GREY_700,
                color=ft.Colors.WHITE,
                label_style=ft.TextStyle(color=ft.Colors.WHITE70),
                border_color=ft.Colors.GREY_600,
                focused_border_color=ft.Colors.BLUE_400
            )

            # Obtener máquinas registradas
            maquinas = obtener_maquinas_licencia(licencia_id)
            maquinas_text = ft.Text(
                f"Máquinas registradas: {len(maquinas)}/{max_maquinas}",
                size=14,
                color=ft.Colors.WHITE70,
                weight="bold"
            )

            # Lista de MACs para este usuario
            macs_lista = ft.Column(
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                height=120
            )

            def actualizar_macs():
                macs_lista.controls.clear()
                maquinas_actualizadas = obtener_maquinas_licencia(licencia_id)
                # Obtener el max_maquinas actualizado de la base de datos
                conn_temp = get_connection()
                cursor_temp = conn_temp.cursor()
                cursor_temp.execute("SELECT max_maquinas FROM licencia WHERE id = ?", (licencia_id,))
                max_actual = cursor_temp.fetchone()["max_maquinas"]
                conn_temp.close()
                
                maquinas_text.value = f"Máquinas registradas: {len(maquinas_actualizadas)}/{max_actual}"
                
                if len(maquinas_actualizadas) == 0:
                    macs_lista.controls.append(
                        ft.Container(
                            padding=15,
                            content=ft.Text(
                                "No hay máquinas registradas",
                                size=12,
                                color=ft.Colors.WHITE54,
                                italic=True,
                                text_align=ft.TextAlign.CENTER
                            ),
                            alignment=ft.Alignment(0, 0)
                        )
                    )
                else:
                    for mac_info in maquinas_actualizadas:
                        mac_id = mac_info["id"]
                        mac_addr = mac_info["mac"]
                        fecha = mac_info["fecha_activacion"]
                        
                        macs_lista.controls.append(
                            ft.Container(
                                padding=10,
                                bgcolor=ft.Colors.GREY_700,
                                border_radius=8,
                                border=ft.border.all(1, ft.Colors.GREY_600),
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text(
                                                    mac_addr,
                                                    size=13,
                                                    color=ft.Colors.WHITE,
                                                    weight="bold"
                                                ),
                                                ft.Text(
                                                    f"Activada: {fecha[:10]}",
                                                    size=11,
                                                    color=ft.Colors.WHITE70
                                                )
                                            ],
                                            expand=True
                                        ),
                                        ft.ElevatedButton(
                                            "Eliminar",
                                            on_click=lambda e, mid=mac_id: eliminar_mac(mid),
                                            bgcolor=ft.Colors.RED_700,
                                            color=ft.Colors.WHITE,
                                            height=35,
                                            width=100,
                                            style=ft.ButtonStyle(
                                                text_style=ft.TextStyle(
                                                    size=13,
                                                    weight="bold"
                                                )
                                            )
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            )
                        )
                page.update()

            def eliminar_mac(mac_id):
                eliminar_maquina_licencia(mac_id)
                actualizar_macs()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("MAC eliminada correctamente"),
                    bgcolor=ft.Colors.GREEN
                )
                page.snack_bar.open = True
                page.update()

            def guardar(e, cliente=cliente, nuevo_cupo=nuevo_cupo, nueva_pass=nueva_pass, lid=licencia_id):
                conn = get_connection()
                cursor = conn.cursor()

                if nuevo_cupo.value:
                    try:
                        nuevo_max = int(nuevo_cupo.value)
                        if nuevo_max < 1:
                            raise ValueError("Debe ser mayor a 0")
                        cursor.execute(
                            "UPDATE licencia SET max_maquinas = ? WHERE id = ?",
                            (nuevo_max, lid)
                        )
                        # Actualizar el valor en el campo también
                        nuevo_cupo.value = str(nuevo_max)
                    except ValueError:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("El valor de máquinas debe ser un número mayor a 0"),
                            bgcolor=ft.Colors.RED
                        )
                        page.snack_bar.open = True
                        page.update()
                        conn.close()
                        return

                if nueva_pass.value:
                    if len(nueva_pass.value) < 4:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("La contraseña debe tener al menos 4 caracteres"),
                            bgcolor=ft.Colors.RED
                        )
                        page.snack_bar.open = True
                        page.update()
                        conn.close()
                        return
                    hash_pass = hashlib.sha256(nueva_pass.value.encode()).hexdigest()
                    cursor.execute(
                        "UPDATE licencia SET password_hash = ? WHERE id = ?",
                        (hash_pass, lid)
                    )
                    nueva_pass.value = ""

                conn.commit()
                conn.close()

                actualizar_macs()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Cuenta actualizada correctamente"),
                    bgcolor=ft.Colors.GREEN
                )
                page.snack_bar.open = True
                page.update()

            # Inicializar lista de MACs
            actualizar_macs()

            # Contenedor expandible para cada licencia
            lista.controls.append(
                ft.Container(
                    padding=15,
                    margin=ft.margin.only(bottom=10),
                    bgcolor=ft.Colors.GREY_800,
                    border_radius=10,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            # Título del usuario
                            ft.Text(
                                cliente,
                                size=18,
                                weight="bold",
                                color=ft.Colors.WHITE
                            ),
                            # Campos de edición
                            ft.Row(
                                controls=[
                                    nuevo_cupo,
                                    nueva_pass,
                                    ft.ElevatedButton(
                                        "Guardar",
                                        on_click=guardar,
                                        bgcolor=ft.Colors.GREEN_700,
                                        color=ft.Colors.WHITE
                                    )
                                ],
                                spacing=10
                            ),
                            # Información de máquinas
                            maquinas_text,
                            # Lista de MACs
                            ft.Container(
                                content=macs_lista,
                                padding=10,
                                bgcolor=ft.Colors.GREY_900,
                                border_radius=8
                            )
                        ]
                    )
                )
            )

    lista = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=0
    )

    refrescar_lista()

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=ft.Colors.GREY_900,
        title=ft.Text(
            "Administración de cuentas",
            size=24,
            weight="bold",
            color=ft.Colors.WHITE
        ),
        content=ft.Container(
            width=750,
            height=550,
            padding=10,
            content=lista
        ),
        actions=[
            ft.TextButton(
                "Cerrar",
                on_click=lambda e: cerrar(),
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE70
                )
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    def cerrar():
        dialog.open = False
        page.update()

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
