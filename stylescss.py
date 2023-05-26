################   NMEA  DIALOG MENU   ##############
nmeadialog = """
    background-color: rgba(100, 102, 100);
    font-family: Arial;
    color: rgba(230, 230, 230);
    border: 2px;
    border-radius: 5px;
    font-size: 10px;
"""

buttons = """
    background-color: rgba(10, 10, 10);
    font-family: Trebuchet MS;
    color: rgba(230, 230, 230);
    border: 4px;
    font-size: 20px;
    border-radius: 5%;
"""

labels = """
    font-family: Arial;
    color: rgba(230, 230, 230);
    font-weight: bold;
    font-size: 15px;
"""

combobox = """
QComboBox {
    background-color: rgba(10, 10, 10, 150);
    font-family: Arial;
    color: rgba(230, 230, 230);
    border: none;
    padding: 1px;
    text-align: center;
    font-size: 14px;
}
QComboBox::drop-down {
    padding-top: 10px;
}
QComboBox::item {
    padding-top: 10px;
}
"""

################   MENU     ##############

menuStyle = """
QMenu {
    background-color: rgba(10, 10, 10, 150);
    font-family: Arial;
    color: rgba(230, 230, 230);
    border: none;
    padding:10px;
    text-align: center;
}
QMenu::item#connect {
    background-color: rgba(10, 10, 10, 150);
    padding:25px;
    text-align: center;
    font-size: 28px;
}
QMenu::item {
    background-color: rgba(10, 10, 10, 150);
    padding:25px;
    text-align: center;
    font-size: 18px;
}
"""

################   MENU BUTTON    ##############

menuButtonStyle = """
QToolButton {
    background-color: rgba(0, 0, 0, 150);
    font-family: MS Shell Dlg 2;
    font-size: 25px;
    font-weight: bold;
    color: rgba(230, 230, 230);
    border: none;
    border-bottom-left-radius: 5%;
}
QToolButton:pressed {
    border-bottom-left-radius: 0%;
}
"""

################   BUTTON  +++++  ##############

buttonZOOMplus = """
    background-color: rgba(0, 0, 0, 150);
    font-family: Arial;
    font-size: 25px;
    font-weight: bold;
    color: rgba(230, 230, 230);
    border: none;
    border-top-left-radius: 5%;
    border-top-right-radius: 5%;
"""

################   BUTTON  ---  ##############

buttonZOOMminus = """
     background-color: rgba(0, 0, 0, 150);
     font-family: Arial;
     font-size: 25px;
     font-weight: bold;
     color: rgba(230, 230, 230);
     border: none;
     border-top-left-radius: 5%;
     border-top-right-radius: 5%;
"""

################   LABEL depth  ##############

labelDepth = """
    font-family: Arial;
    font-size: 55px;
    font-weight: bold;
    color: rgba(0, 0, 0);
    border: none;
"""

labelLetterDepth = """
    font-family: Arial;
    font-size: 17px;
    font-weight: bold;
    color: rgba(0, 0, 0);
    border: none;
"""

################   LABEL info  ##############

labelInfo = """
    background-color: rgba(0, 0, 0, 150);
    font-family: Swis721 Cn BT;
    font-size: 20px;
    font-weight: bold;
    border: none;
    color: rgba(230, 230, 230);
    padding-left: 10px;
    font-smooth: 2em;
"""
labelInfoRight = """
    background-color: transparent;
    font-family: Swis721 Cn BT;
    font-size: 20px;
    font-weight: bold;
    border: none;
    color: rgba(230, 230, 230);
    padding-right: 5px;
    font-smooth: 2em;
"""

labelInfoTop = """
    background-color: rgba(0, 0, 0, 150);
    font-family: Swis721 BlkCn BT;
    font-size: 20px;
    color: rgba(230, 230, 230);
    border-top-right-radius: 10%;
    padding-left: 10px;
"""
labelInfoTopRight = """
    background-color: transparent;
    font-family: Swis721 BlkCn BT;
    font-size: 20px;
    color: rgba(230, 230, 230);
    border-top-right-radius: 10%;
    text-align: right;
    padding-right: 5px;
"""

### Fonts: Franklin Gothic Book; Arial; Lucida Fax; Trebuchet MS; Times New Roman;
### Tw Cen MT Condensed - вытянутый!
### Swis721 Cn BT - прикольный!      background-color: transparent;