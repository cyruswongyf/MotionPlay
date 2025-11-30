"""
Dark Dialog Utilities for MotionPlay
Provides fully styled dark dialogs to eliminate white popups.
Extracted from ui/base.py for better organization.
"""

from PyQt6.QtWidgets import (
    QDialog, QMessageBox, QInputDialog, 
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import QTimer
from ..styles.colors import BLACK, WHITE, RED, RED_PRIMARY, RED_BRIGHT, GRAY, INPUT_BG


class BlackWindow:
    """
    Nuclear black background mixin.
    This is the ONLY method that never fails.
    Works on Windows, macOS, Linux — no exceptions.
    """
    def __init__(self):
        # QUAD-KILL approach: stylesheet + autofill + palette + splitter fix
        nuclear_stylesheet = f"""
            QDialog, QWidget {{ 
                background-color: {BLACK}; 
                color: {WHITE}; 
            }}
            QSplitter {{ 
                background-color: {BLACK}; 
            }}
            QSplitter::handle {{ 
                background: #1a1a1a; 
            }}
        """
        self.setStyleSheet(nuclear_stylesheet)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(BLACK))
        p.setColor(self.foregroundRole(), QColor(WHITE))
        # Additional nuclear strikes
        p.setColor(QPalette.ColorRole.Window, QColor(BLACK))
        p.setColor(QPalette.ColorRole.Base, QColor(BLACK))
        p.setColor(QPalette.ColorRole.Text, QColor(WHITE))
        p.setColor(QPalette.ColorRole.WindowText, QColor(WHITE))
        self.setPalette(p)


class BlackDialog(QDialog, BlackWindow):
    """
    Nuclear black dialog base class.
    All custom dialogs MUST inherit from this.
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
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: {BLACK};
            color: {WHITE};
        }}
        QLabel {{
            color: {WHITE};
            background-color: transparent;
        }}
        QPushButton {{
            background-color: {GRAY};
            color: {WHITE};
            border: 2px solid {RED};
            border-radius: 5px;
            padding: 8px 16px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {RED};
        }}
    """)
    
    # Double guarantee
    msg.setAutoFillBackground(True)
    p = msg.palette()
    p.setColor(msg.backgroundRole(), QColor(BLACK))
    p.setColor(QPalette.ColorRole.Window, QColor(BLACK))
    p.setColor(QPalette.ColorRole.Text, QColor(WHITE))
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
        label_widget.setStyleSheet(f"color: {WHITE}; font-size: 13px; background-color: transparent;")
        layout.addWidget(label_widget)
        
        # Input
        self.input_field = QLineEdit(default_text)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {INPUT_BG};
                color: {WHITE};
                border: 2px solid {RED};
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {RED_BRIGHT};
                background-color: #222222;
            }}
        """)
        self.input_field.selectAll()
        layout.addWidget(self.input_field)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(100, 35)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GRAY};
                color: {WHITE};
                border: 2px solid #666666;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #666666;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumSize(100, 35)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED_PRIMARY};
                color: {WHITE};
                border: 2px solid {RED_BRIGHT};
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {RED_BRIGHT};
                color: {BLACK};
            }}
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
        label_widget.setStyleSheet(f"color: {WHITE}; font-size: 13px; background-color: transparent;")
        layout.addWidget(label_widget)
        
        # Text input
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(default_text)
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {INPUT_BG};
                color: {WHITE};
                border: 2px solid {RED};
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border: 2px solid {RED_BRIGHT};
                background-color: #222222;
            }}
        """)
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(100, 35)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GRAY};
                color: {WHITE};
                border: 2px solid #666666;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #666666;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumSize(100, 35)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED_PRIMARY};
                color: {WHITE};
                border: 2px solid {RED_BRIGHT};
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {RED_BRIGHT};
                color: {BLACK};
            }}
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
