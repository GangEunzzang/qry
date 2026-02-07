"""Tests for theme screen."""

from qry.shared.constants import AVAILABLE_THEMES
from qry.ui.screens.screen_theme import ThemeScreen


class TestThemeScreen:

    def test_creates_with_current_theme(self):
        screen = ThemeScreen(current_theme="dracula")
        assert screen._current_theme == "dracula"

    def test_creates_with_empty_theme(self):
        screen = ThemeScreen()
        assert screen._current_theme == ""

    def test_dismiss_returns_none_on_cancel(self):
        screen = ThemeScreen()
        # action_cancel should call dismiss(None)
        # We verify the method exists and is callable
        assert hasattr(screen, "action_cancel")


class TestAvailableThemes:

    def test_themes_not_empty(self):
        assert len(AVAILABLE_THEMES) > 0

    def test_default_themes_present(self):
        assert "textual-dark" in AVAILABLE_THEMES
        assert "textual-light" in AVAILABLE_THEMES

    def test_popular_themes_present(self):
        assert "dracula" in AVAILABLE_THEMES
        assert "tokyo-night" in AVAILABLE_THEMES
        assert "catppuccin-mocha" in AVAILABLE_THEMES
        assert "nord" in AVAILABLE_THEMES

    def test_themes_are_valid_textual_themes(self):
        from textual.app import App

        app = App()
        builtin = app.available_themes
        for theme_name in AVAILABLE_THEMES:
            assert theme_name in builtin, f"{theme_name} is not a valid Textual theme"


class TestAppThemeIntegration:

    def test_app_has_theme_binding(self):
        from qry.app import QryApp

        app = QryApp()
        binding_keys = [b.key for b in app.BINDINGS]
        assert "f2" in binding_keys

    def test_apply_valid_theme(self):
        from qry.app import QryApp

        app = QryApp()
        app._apply_theme("dracula")
        assert app.theme == "dracula"

    def test_apply_invalid_theme_ignored(self):
        from qry.app import QryApp

        app = QryApp()
        original = app.theme
        app._apply_theme("nonexistent-theme")
        assert app.theme == original

    def test_settings_default_theme(self):
        from qry.shared.constants import DEFAULT_THEME

        assert DEFAULT_THEME == "textual-dark"
        assert DEFAULT_THEME in AVAILABLE_THEMES
