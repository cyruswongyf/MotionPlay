"""
MotionPlay v3.0 "MotionForge" — THE FINAL BOSS PATCH
Nuclear Solution for Black Backgrounds — Works on EVERY dialog, EVERY platform
Auto-applies black styles to ALL widgets.
"""

from PyQt6.QtWidgets import (
    QDialog, QMainWindow, QMessageBox, QPushButton,
    QLineEdit, QTextEdit, QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QTimer


class BlackWindow:
    """
    Nuclear black background mixin.
    This is the ONLY method that never fails.
    Works on Windows, macOS, Linux — no exceptions.
    ABSOLUTE FINAL VERSION: Kills ALL white backgrounds including QSplitter gaps.
    """
    def __init__(self):
        # QUAD-KILL approach: stylesheet + autofill + palette + splitter fix
        nuclear_stylesheet = """
            QDialog, QWidget { 
                background-color: #0d0d0d; 
                color: white; 
            }
            QSplitter { 
                background-color: #0d0d0d; 
            }
            QSplitter::handle { 
                background: #1a1a1a; 
            }
        """
        self.setStyleSheet(nuclear_stylesheet)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor("#0d0d0d"))
        p.setColor(self.foregroundRole(), QColor("#ffffff"))
        # Additional nuclear strikes
        p.setColor(QPalette.ColorRole.Window, QColor("#0d0d0d"))
        p.setColor(QPalette.ColorRole.Base, QColor("#0d0d0d"))
        p.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
        self.setPalette(p)


class BlackDialog(QDialog, BlackWindow):
    """
    Nuclear black dialog base class.
    All custom dialogs MUST inherit from this.
    Auto-applies black styles to all child widgets.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BlackWindow.__init__(self)
        # Delayed auto-styling after UI is built
        QTimer.singleShot(0, self._apply_black_styles_to_children)
    
    def _apply_black_styles_to_children(self):
        """Auto-apply black styles to all child widgets."""
        from .styles.black_theme import UNIVERSAL_BLACK_STYLESHEET
        
        # Apply universal stylesheet to dialog
        current_style = self.styleSheet()
        if "QPushButton" not in current_style:  # Don't override if already styled
            self.setStyleSheet(current_style + "\n" + UNIVERSAL_BLACK_STYLESHEET)


class BlackMainWindow(QMainWindow, BlackWindow):
    """
    Nuclear black main window base class.
    Main application window MUST inherit from this.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BlackWindow.__init__(self)


def create_black_message_box(parent, icon, title, text, buttons=QMessageBox.StandardButton.Ok):
    """
    Create a QMessageBox with guaranteed black background.
    
    Args:
        parent: Parent widget
        icon: QMessageBox.Icon (Information, Warning, Critical, Question)
        title: Window title
        text: Message text
        buttons: Standard buttons
    
    Returns:
        QMessageBox instance with nuclear black background
    """
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(buttons)
    
    # Nuclear black stylesheet
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #0d0d0d;
            color: white;
        }
        QLabel {
            color: white;
            background-color: transparent;
        }
        QPushButton {
            background-color: #333333;
            color: white;
            border: 2px solid #ff1a1a;
            border-radius: 5px;
            padding: 8px 16px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #ff1a1a;
        }
    """)
    
    # Double guarantee
    msg.setAutoFillBackground(True)
    p = msg.palette()
    p.setColor(msg.backgroundRole(), QColor("#0d0d0d"))
    p.setColor(QPalette.ColorRole.Window, QColor("#0d0d0d"))
    p.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
    msg.setPalette(p)
    
    return msg


def show_info(parent, title, message):
    """Show info message with black background."""
    msg = create_black_message_box(parent, QMessageBox.Icon.Information, title, message)
    return msg.exec()


def show_warning(parent, title, message):
    """Show warning message with black background."""
    msg = create_black_message_box(parent, QMessageBox.Icon.Warning, title, message)
    return msg.exec()


def show_error(parent, title, message):
    """Show error message with black background."""
    msg = create_black_message_box(parent, QMessageBox.Icon.Critical, title, message)
    return msg.exec()


def show_question(parent, title, message):
    """Show question dialog with black background."""
    msg = create_black_message_box(
        parent,
        QMessageBox.Icon.Question,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    return msg.exec()


# ============================================================================
# BLACK INPUT DIALOGS (Replace QInputDialog)
# ============================================================================

class BlackInputDialog(BlackDialog):
    """
    Black-themed input dialog.
    Replacement for QInputDialog with guaranteed black background.
    """
    def __init__(self, parent=None, title="Input", label="Enter value:", default_text=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.result_text = default_text
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: white; font-size: 13px; background-color: transparent;")
        layout.addWidget(label_widget)
        
        # Input
        self.input_field = QLineEdit(default_text)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #ff1a1a;
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #ff4444;
                background-color: #222222;
            }
        """)
        self.input_field.selectAll()
        layout.addWidget(self.input_field)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: 2px solid #666666;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumSize(100, 35)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff1a1a;
                color: white;
                border: 2px solid #ff4444;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: black;
            }
        """)
        ok_btn.clicked.connect(self._on_ok)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        self.input_field.setFocus()
    
    def _on_ok(self):
        """Handle OK button."""
        self.result_text = self.input_field.text()
        self.accept()
    
    def get_text(self):
        """Get the entered text."""
        return self.result_text
    
    @staticmethod
    def get_text_input(parent, title, label, default_text=""):
        """
        Static method to get text input (replacement for QInputDialog.getText).
        
        Returns:
            tuple: (text, ok) where ok is True if user clicked OK
        """
        dialog = BlackInputDialog(parent, title, label, default_text)
        result = dialog.exec()
        return (dialog.get_text(), result == QDialog.DialogCode.Accepted)


class BlackMultiLineInputDialog(BlackDialog):
    """
    Black-themed multi-line input dialog.
    Replacement for QInputDialog.getMultiLineText.
    """
    def __init__(self, parent=None, title="Input", label="Enter text:", default_text=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 350)
        
        self.result_text = default_text
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: white; font-size: 13px; background-color: transparent;")
        layout.addWidget(label_widget)
        
        # Text input
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(default_text)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #ff1a1a;
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #ff4444;
                background-color: #222222;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: 2px solid #666666;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumSize(100, 35)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff1a1a;
                color: white;
                border: 2px solid #ff4444;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: black;
            }
        """)
        ok_btn.clicked.connect(self._on_ok)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        self.text_edit.setFocus()
    
    def _on_ok(self):
        """Handle OK button."""
        self.result_text = self.text_edit.toPlainText()
        self.accept()
    
    def get_text(self):
        """Get the entered text."""
        return self.result_text
    
    @staticmethod
    def get_multi_line_text_input(parent, title, label, default_text=""):
        """
        Static method to get multi-line text input.
        
        Returns:
            tuple: (text, ok) where ok is True if user clicked OK
        """
        dialog = BlackMultiLineInputDialog(parent, title, label, default_text)
        result = dialog.exec()
        return (dialog.get_text(), result == QDialog.DialogCode.Accepted)
