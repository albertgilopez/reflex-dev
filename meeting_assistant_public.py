from rxconfig import config

import reflex as rx
from meeting_assistant import style

import meeting_transcriptions
import meeting_tasks

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI()

docs_url = "https://github.com/albertgilopez"
linkedin_url = "https://www.linkedin.com/in/albertgilopez/"

class State(rx.State):
    """The app state."""

    # Lista para almacenar los resultados de las transcripciones

    transcriptions: list[str] = []
    summary: list[str] = []
    actionable_items: list[str] = []

     # Lista para almacenar mensajes de estado
    status_messages: list[str] = []

    uploaded_file_path: str = None  # Variable para almacenar la ruta del archivo subido

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la carga de archivos de audio."""

        for file in files:
            self.status_messages.append(f"Archivo {file.filename} cargado correctamente.")

            upload_data = await file.read()
            outfile = rx.get_asset_path(file.filename)

            # Guardar el archivo de audio
            with open(outfile, "wb") as file_object:
                file_object.write(upload_data)

            # Almacenar la ruta del archivo subido
            self.uploaded_file_path = outfile


    async def handle_transcription(self):
        """Maneja la transcripción de archivos de audio."""

        if self.uploaded_file_path is not None:
            transcription = meeting_transcriptions.transcribe_audio(self.uploaded_file_path)
            self.transcriptions.append(transcription)
        else:
            self.status_messages.append("No hay archivo cargado para transcribir.")

    async def generate_summary(self):
        """Genera un resumen de la reunión."""

        summary = meeting_tasks.summarize_meeting(self.transcriptions[0])
        self.summary.append(summary)

    async def generate_insights(self):
        """Genera insights y puntos clave de la reunión."""

        actionable_items = meeting_tasks.get_actionable_items(self.transcriptions[0])
        self.actionable_items.append(actionable_items)
        
color = "rgb(107,99,246)"

def index() -> rx.Component:

    chat_examples = [
        "Asistente de IA que transcribe, resume y extrae insights de reuniones.",
    ]

    return rx.vstack(
            # rx.color_mode_button(rx.color_mode_icon(), float="right"),
            rx.vstack(
                rx.heading("Meeting Assistant", font_size="2em"),
                *[rx.box(rx.text(example, style={"font-size": "1em", "font-style": "italic", "padding-top":"1em"})) for example in chat_examples],
            ),
            rx.upload(
                rx.vstack(
                    rx.button(
                        "Selecciona un archivo",
                        color=color,
                        bg="white",
                        border=f"1px solid {color}",
                    ),
                    rx.text(
                        "\nArrastra y suelta tu reunión en video o audio aquí, o haz click para seleccionarla."
                    ),
                    margin="10px",
                ),
                multiple=True,
                accept={
                    "video/mp4": [".mp4"],
                },
                max_files=1,
                disabled=False,
                on_keyboard=True,
                border=f"1px dotted {color}",
                padding="10px",
            ),
            rx.button(
                "Procesar Archivo",
                on_click=lambda: State.handle_upload(
                    rx.upload_files()
                ),
                style=style.button_style,
                marggin_bottom="10px"
            ),
            
            rx.button_group(
                # Botón para la transcripción
                rx.button(
                    "Transcribir",
                    on_click=lambda: State.handle_transcription(),
                    style=style.button_style
                ),

                # Botón para generar resumen
                rx.button(
                    "Generar Resumen",
                    on_click=lambda: State.generate_summary(),
                    style=style.button_style
                ),

                # Botón para generar insights y puntos clave
                rx.button(
                    "Generar Insights",
                    on_click=lambda: State.generate_insights(),
                    style=style.button_style
                ),
            ),

            rx.responsive_grid(
                # Componente para mostrar mensajes de estado como alertas
                rx.foreach(
                    State.status_messages,
                    lambda message: rx.alert(
                        rx.alert_icon(),
                        rx.alert_title(message),
                        status="info" 
                    )
                ),
            ),

            rx.responsive_grid(
                rx.foreach(
                    State.transcriptions,
                    lambda transcription: rx.box(
                        rx.text("TRANSCRIPCIÓN:\n"),
                        rx.text(transcription),
                        padding="1em",
                        border="1px solid #ddd",
                        margin="1em 0"
                    )
                ),
                rx.foreach(
                    State.summary,
                    lambda summary: rx.box(
                        rx.text("RESUMEN:\n"),
                        rx.text(summary),
                        padding="1em",
                        border="1px solid #ddd",
                        margin="1em 0"
                    )
                ),
                rx.foreach(
                    State.actionable_items,
                    lambda actionable_items: rx.box(
                        rx.text("PUNTOS CLAVE:\n"),
                        rx.text(actionable_items),
                        padding="1em",
                        border="1px solid #ddd",
                        margin="1em 0"
                    )
                ),
            ),

            rx.link(
                "Check out me GitHub for more projects",
                href=docs_url,
                border="0.1em solid",
                padding="0.5em",
                border_radius="0.5em",
                font_size="0.8em",
                _hover={
                    "color": rx.color_mode_cond(
                        light="rgb(107,99,246)",
                        dark="rgb(179, 175, 255)",
                    )
                },
            ),
            rx.link(
                "Reach me out on Linkedin (Albert Gil López)",
                href=linkedin_url,
                border="0.1em solid",
                padding="0.5em",
                border_radius="0.5em",
                font_size="0.8em",
                _hover={
                    "color": rx.color_mode_cond(
                        light="rgb(107,99,246)",
                        dark="rgb(179, 175, 255)",
                    )
                },
            ),

            font_size="1em",
            padding_top="10%",
            margin_bottom="10%",
            padding="5em",
        )

# Add state and page to the app.
app = rx.App()
app.add_page(index)
app.compile()
