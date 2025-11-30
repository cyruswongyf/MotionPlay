"""
Dark-themed dialog utilities for MotionForge
Provides fully styled dark dialogs to eliminate white popups
"""

from PyQt6.QtWidgets import QInputDialog, QMessageBox, QDialog
from PyQt6.QtGui import QColor, QPalette


def dark_input_dialog(parent, title, label, text=""):
    """
    Create a dark-themed input dialog
    
    Args:
        parent: Parent widget
        title: Dialog window title
        label: Label text for the input field
        text: Default text value
        
    Returns:
        QInputDialog configured with dark theme
    """
    dialog = QInputDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    dialog.setTextValue(text)
    dialog.setStyleSheet("""
        QInputDialog { 
            background-color: #0d0d0d; 
            color: white; 
        }
        QLabel { 
            color: white; 
            font-size: 13px;
        }
        QLineEdit { 
            background-color: #1a1a1a; 
            color: white; 
            border: 2px solid #ff1a1a; 
            padding: 5px;
            border-radius: 3px;
        }
        QLineEdit:focus {
            border: 2px solid #ff3333;
        }
        QPushButton { 
            background-color: #1a1a1a; 
            color: white; 
            border: 2px solid #ff1a1a; 
            padding: 6px 15px;
            border-radius: 3px;
            font-weight: bold;
        }
        QPushButton:hover { 
            background-color: #ff1a1a; 
            color: black; 
        }
        QPushButton:pressed {
            background-color: #cc0000;
        }
    """)
    
    # Force dark background using palette
    dialog.setAutoFillBackground(True)
    palette = dialog.palette()
    palette.setColor(dialog.backgroundRole(), QColor("#0d0d0d"))
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d0d0d"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
    dialog.setPalette(palette)
    
    return dialog


def dark_message_box(parent, title, text, buttons=QMessageBox.StandardButton.Ok, icon=QMessageBox.Icon.NoIcon):
    """
    Create a dark-themed message box
    
    Args:
        parent: Parent widget
        title: Dialog window title
        text: Message text
        buttons: Standard buttons to display
        icon: Message box icon
        
    Returns:
        QMessageBox configured with dark theme
    """
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(buttons)
    msg.setIcon(icon)
    msg.setStyleSheet("""
        QMessageBox { 
            background-color: #0d0d0d; 
            color: white; 
        }
        QLabel { 
            color: white; 
            font-size: 13px;
        }
        QPushButton { 
            background-color: #1a1a1a; 
            color: white; 
            border: 2px solid #ff1a1a; 
            padding: 6px 15px; 
            border-radius: 3px;
            font-weight: bold;
            min-width: 70px;
        }
        QPushButton:hover { 
            background-color: #ff1a1a; 
            color: black; 
        }
        QPushButton:pressed {
            background-color: #cc0000;
        }
    """)
    
    # Force dark background using palette
    msg.setAutoFillBackground(True)
    palette = msg.palette()
    palette.setColor(msg.backgroundRole(), QColor("#0d0d0d"))
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d0d0d"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
    msg.setPalette(palette)
    
    return msg
