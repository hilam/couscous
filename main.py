import os
os.environ['KIVY_TEXT'] = 'sdl2'
import kivy
kivy.require("1.9.0")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel

kvcode = """
BoxLayout:
    orientation: 'vertical'
    padding: 5
    spacing: 5

    # escolha inscrição e pesquisa
    BoxLayout:
        orientation: 'horizontal'
        padding: 2
        spacing: 2
        size_hint_y: 0.40

        BoxLayout:
            orientation: 'vertical'
            padding: 2
            spacing: 2
            size_hint_x: 0.5

            BoxLayout:
                orientation: 'vertical'
                Label:
                    text: "Escolha inscrição/categoria"
                    font_name: "fonts/DejaVuSans.ttf"
                    font_size: 18
                BoxLayout:
                    orientation: 'horizontal'
                    # combo de inscrições
                    TextInput:
                        multiline: False
                        size_hint_x: 1
                    Button:
                        text: 'OK'
                        on_release: print("A implementar...")
                        size_hint_x: 0.2
                    Button:
                        text: 'ADD'
                        on_release: print("A implementar...")
                        size_hint_x: 0.2
                Label:
                    text: "[ ] Checkbox 'abrir em nova aba'"
                    font_name: "fonts/LiberationSans-Regular.ttf"
                    font_size: 16

        BoxLayout:
            orientation: 'vertical'
            padding: 10
            spacing: 16
            size_hint_x: 0.5
            Label:
                text: "Pesquisa"
                font_name: "fonts/DejaVuSans.ttf"
                font_size: 18
            # caixa de pesquisa
            Button:
                text: 'Pesquisa'
                on_release: print("A implementar pesquisa...")

    # feeds
    BoxLayout:
        id: feeds
        TabbedPanel:
            canvas.before:
                Color:
                    rgba: 1., 0., 0., .3
                Rectangle:
                    pos: self.pos
                    size: self.size

            TabbedPanelItem:
                text: 'first tab'
                Label:
                    text: 'First tab content area'
                    font_name: "fonts/DejaVuSans.ttf"
                    font_size: 18
            TabbedPanelItem:
                text: 'tab2'
                BoxLayout:
                    Label:
                        text: 'Second tab content area'
                        font_name: "fonts/DejaVuSans.ttf"
                        font_size: 14
                    Button:
                        text: 'Button that does nothing'
            TabbedPanelItem:
                text: 'tab3'
                RstDocument:
                    text:
                        '\\n'.join(("Hello world", "-----------",
                        "You are in the third tab."))

    # barra de status
    BoxLayout:
        id: status_bar
        pos_hint: {'y': 0}
        size_hint_y: 0.10
        Label:
            text: 'Barra de status'
"""


class Couscous(App):

    def build(self):
        self.title = 'Couscous - Leitor de Feeds'
        return Builder.load_string(kvcode)

if __name__== '__main__':
    Couscous().run()
