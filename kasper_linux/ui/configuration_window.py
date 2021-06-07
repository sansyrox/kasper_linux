import os
import logging
import gi
gi.require_version('Gtk', '3.0')  # nopep8
from pathlib import Path
from gi.repository import Gtk
from .login_window import LoginWindow
from kasper_config import kasperConfig

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
kaspercfg = kasperConfig()

#
# WARNING!!!!
# This order needs to be synced with glade_files/configure.glade
# which defines the actual strings and entries in the list!!!!
STT_DEEPSPEECH=0
STT_VOSK=1
STT_GOOGLE=2
STT_WATSON=3
STT_BING=4

TTS_FLITE=0
TTS_GOOGLE=1
TTS_WATSON=2

HOTWORD_SNOWBOY=0
HOTWORD_POCKETSPHINX=1
HOTWORD_NONE=2

class WatsonCredentialsDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Enter Credentials", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        username_field = Gtk.Entry()
        username_field.set_placeholder_text("Username")
        password_field = Gtk.Entry()
        password_field.set_placeholder_text("Password")
        password_field.set_visibility(False)
        password_field.set_invisible_char('*')

        self.username_field = username_field
        self.password_field = password_field

        box = self.get_content_area()

        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        box.set_spacing(10)

        box.add(username_field)
        box.add(password_field)
        self.show_all()


class BingCredentialDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Enter API Key", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        api_key_field = Gtk.Entry()
        api_key_field.set_placeholder_text("API Key")

        self.api_key_field = api_key_field

        box = self.get_content_area()

        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        box.set_spacing(10)

        box.add(api_key_field)
        self.show_all()


class ConfigurationWindow:
    def __init__(self) -> None:
        super().__init__()
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(
            TOP_DIR, "glade_files/configure.glade"))

        self.window = builder.get_object("configuration_window")
        self.stt_combobox = builder.get_object("stt_combobox")
        self.tts_combobox = builder.get_object("tts_combobox")
        self.auth_switch = builder.get_object("auth_switch")
        self.hotword_combobox = builder.get_object("hotword_combobox")
        self.wake_button_switch = builder.get_object("wake_button_switch")

        self.init_auth_switch()
        self.init_tts_combobox()
        self.init_stt_combobox()
        self.init_hotword_switch()
        self.init_wake_button_switch()

        builder.connect_signals(ConfigurationWindow.Handler(self))
        self.window.set_resizable(False)

    def show_window(self):
        self.window.show_all()
        Gtk.main()

    def exit_window(self):
        self.window.destroy()
        Gtk.main_quit()

    def init_tts_combobox(self):
        default_tts = kaspercfg.get('tts')
        if default_tts == 'google':
            self.tts_combobox.set_active(TTS_GOOGLE)
        elif default_tts == 'flite':
            self.tts_combobox.set_active(TTS_FLITE)
        elif default_tts == 'watson':
            self.tts_combobox.set_active(TTS_WATSON)
        else:
            self.tts_combobox.set_active(TTS_FLITE)
            kaspercfg.set('tts', 'flite')

    def init_stt_combobox(self):
        default_stt = kaspercfg.get('stt')
        if default_stt == 'google':
            self.stt_combobox.set_active(STT_GOOGLE)
        elif default_stt == 'watson':
            self.stt_combobox.set_active(STT_WATSON)
        elif default_stt == 'bing':
            self.stt_combobox.set_active(STT_BING)
        elif default_stt == 'deepspeech-local':
            self.stt_combobox.set_active(STT_DEEPSPEECH)
        elif default_stt == 'vosk':
            self.stt_combobox.set_active(STT_VOSK)
        else:
            self.tts_combobox.set_active(STT_DEEPSPEECH)
            kaspercfg.set('stt', 'deepspeech-local')

    def init_auth_switch(self):
        usage_mode = kaspercfg.get('kasper.mode')
        if usage_mode == 'authenticated':
            self.auth_switch.set_active(True)
        else:
            self.auth_switch.set_active(False)

    def init_hotword_switch(self):
        default_hotword = kaspercfg.get('hotword.engine')
        if default_hotword == 'Snowboy':
            self.hotword_combobox.set_active(HOTWORD_SNOWBOY)
        elif default_hotword == 'PocketSphinx':
            self.hotword_combobox.set_active(HOTWORD_POCKETSPHINX)
        elif default_hotword == 'None':
            self.hotword_combobox.set_active(HOTWORD_NONE)
        else:
            try:
                import snowboy
                self.hotword_combobox.set_active(HOTWORD_SNOWBOY)
                kaspercfg.set('hotword.engine', 'Snowboy')
            except ImportError:
                self.hotword_combobox.set_active(HOTWORD_POCKETSPHINX)
                kaspercfg.set('hotword.engine', 'PocketSphinx')

    def init_wake_button_switch(self):
        try:
            import RPi.GPIO
            if kaspercfg.get('wakebutton') == 'enabled':
                self.wake_button_switch.set_active(True)
            else:
                self.wake_button_switch.set_active(False)
        except ImportError:
            self.wake_button_switch.set_sensitive(False)
        except RuntimeError:
            self.wake_button_switch.set_sensitive(False)

    class Handler:
        def __init__(self, config_window):
            self.config_window = config_window

        def on_delete_window(self, *args):
            self.config_window.exit_window()

        def on_stt_combobox_changed(self, combo: Gtk.ComboBox):
            selection = combo.get_active()

            if selection == STT_DEEPSPEECH:
                kaspercfg.set('stt', 'deepspeech_local')

            elif selection == STT_VOSK:
                kaspercfg.set('stt', 'vosk')

            elif selection == STT_GOOGLE:
                kaspercfg.set('stt', 'google')

            elif selection == STT_WATSON:
                credential_dialog = WatsonCredentialsDialog(
                    self.config_window.window)
                response = credential_dialog.run()

                if response == Gtk.ResponseType.OK:
                    username = credential_dialog.username_field.get_text()
                    password = credential_dialog.password_field.get_text()
                    kaspercfg.set('stt', 'watson')
                    kaspercfg.set('watson.stt.user', username)
                    kaspercfg.set('watson.stt.pass', password)
                else:
                    self.config_window.init_stt_combobox()

                credential_dialog.destroy()

            elif selection == STT_BING:
                credential_dialog = BingCredentialDialog(
                    self.config_window.window)
                response = credential_dialog.run()

                if response == Gtk.ResponseType.OK:
                    api_key = credential_dialog.api_key_field.get_text()
                    kaspercfg.set('stt', 'bing')
                    kaspercfg.set('bing.api', api_key)
                else:
                    self.config_window.init_stt_combobox()

                credential_dialog.destroy()

        def on_tts_combobox_changed(self, combo):
            selection = combo.get_active()

            if selection == TTS_GOOGLE:
                kaspercfg.set('tts', 'google')

            elif selection == TTS_FLITE:
                kaspercfg.set('tts', 'flite')

            elif selection == TTS_WATSON:
                credential_dialog = WatsonCredentialsDialog(
                    self.config_window.window)
                response = credential_dialog.run()

                if response == Gtk.ResponseType.OK:
                    username = credential_dialog.username_field.get_text()
                    password = credential_dialog.password_field.get_text()
                    kaspercfg.set('tts', 'watson')
                    kaspercfg.set('watson.tts.user', username)
                    kaspercfg.set('watson.tts.pass', password)
                    kaspercfg.set('watson.tts.voice', 'en-US_AllisonVoice')
                else:
                    self.config_window.init_tts_combobox()
                credential_dialog.destroy()

        def on_auth_switch_active_notify(self, switch, gparam):
            if switch.get_active():
                login_window = LoginWindow()
                login_window.show_window()
                if kaspercfg.get('kasper.mode') == 'authenticated':
                    switch.set_active(True)
                else:
                    switch.set_active(False)

        def on_hotword_combobox_changed(self, combo: Gtk.ComboBox):
            selection = combo.get_active()

            if selection == HOTWORD_SNOWBOY:
                kaspercfg.set('hotword.engine', 'Snowboy')
            elif selection == HOTWORD_POCKETSPHINX:
                kaspercfg.set('hotword.engine', 'PocketSphinx')
            elif selection == HOTWORD_NONE:
                kaspercfg.set('hotword.engine', 'None')


        def on_wake_button_switch_active_notify(self, switch, gparam):
            if switch.get_active():
                kaspercfg.set('wakebutton', 'enabled')
            else:
                kaspercfg.set('wakebutton', 'disabled')
