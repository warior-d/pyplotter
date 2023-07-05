################   POINT  DIALOG MENU   ##############

keyboard = """
    color: rgba(255, 255, 255);
    font-size: 18px;
"""

lay = """
    border: 1px solid rgba(50, 50, 50, 120); 
"""

iconFish = """
QPushButton:pressed {
    border: 2px solid rgba(255, 215, 0);
}
"""

################   MAP  DIALOG MENU   ##############
map_dialog = """
    background-color: rgba(55,85,112);
    font-family: Arial;
    color: rgba(230, 230, 230);
"""

map_button = """
    background-color: rgba(86,98,111);
    font-family: Arial;
    color: rgba(230, 230, 230);
    font-size: 18px;
    border: 1px solid rgba(50, 50, 50, 120); 
"""

group_box = """
    background-color: rgba(53,57,63);
    font-family: Arial;
    color: rgba(230, 230, 230);
    font-size: 10px;
    border: 0px;
"""

group_box_label = """
    font-family: Arial;
    color: rgba(230, 230, 230);
    font-size: 15px;
"""

combo_box = """
    font-family: Arial;
    background-color: rgba(29,46,62);
    color: rgba(230, 230, 230);
    font-size: 15px;
"""


################   NMEA  DIALOG MENU   ##############
nmeadialog = """
    background-color: rgba(53,57,63);
    font-family: Arial;
    color: rgba(230, 230, 230);
    border: 2px;
    font-size: 10px;
"""

buttons = """
    background-color: rgba(86,98,111);
    font-family: Arial;
    color: rgba(230, 230, 230);
    font-size: 18px;
    border: 1px solid rgba(50, 50, 50, 120); 
"""

labels = """
    font-family: Arial;
    color: rgba(182,186,191);
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
    text-align: center;
}
QMenu::item {
    background-color: rgba(10, 10, 10, 150);
    padding-top:25px;
    padding-bottom:25px;
    padding-left:15px;
    padding-right:20px;
    text-align: center;
    font-size: 18px;
    border-bottom: 1px solid rgba(50, 50, 50, 180); 
}
"""
#rgba(77, 77, 77, 180)
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
"""
labelInfoRight = """
    background-color: transparent;
    font-family: Swis721 Cn BT;
    font-size: 20px;
    font-weight: bold;
    border: none;
    color: rgba(230, 230, 230);
    padding-right: 5px;
"""
labelInfoRightYes = """
    background-color: transparent;
    font-family: Swis721 Cn BT;
    font-size: 20px;
    font-weight: bold;
    border: none;
    color: rgba(80, 200, 120);
    padding-right: 5px;
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