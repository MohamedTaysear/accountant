import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont, QPalette, QColor

import database
import auth
from ui.login_window import LoginWindow
from ui import theme
from ui.theme import LightTheme


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Store Accounting System")

    theme.set_theme(LightTheme())
    app.setFont(QFont(theme._active.font_family, theme._active.size_normal))
    app.setStyleSheet(theme.build_app_stylesheet())

    # Set palette colors that QSS cannot reliably override on Windows
    palette = app.palette()
    palette.setColor(QPalette.PlaceholderText, QColor(theme._active.text_placeholder))
    palette.setColor(QPalette.ToolTipBase, QColor(theme._active.nav_bg))
    palette.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))
    app.setPalette(palette)

    try:
        database.initialize_database()
        auth.seed_default_admin()
    except Exception:
        print(traceback.format_exc())
        QMessageBox.critical(
            None,
            "Startup Error",
            "Failed to initialize the database.\n\nThe application will now exit."
        )
        sys.exit(1)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
