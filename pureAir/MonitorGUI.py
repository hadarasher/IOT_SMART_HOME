import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import datetime
from init import *
from MQTT_client import *

# Creating Client name - should be unique
global clientname
r = random.randrange(1, 100000)
clientname = "pureair-" + class_ID + "-" + str(r)
global pub_topic, sub_topics
pub_topic = relay_topic
sub_topics = [DHT_topic, AQS_topic]
global IS_AUTO, IS_OPEN
IS_AUTO = True  # tells if the windows will be controlled automatically of manual by the teacher
IS_OPEN = False  # tells if windows are open or closed. As default will be close


class MC(Mqtt_client):
    def __init__ (self):
        super().__init__()

    def on_message (self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        ic("message from:" + topic, m_decode)
        try:
            mainwin.StatusDock.handleMessage(topic, m_decode)
        except:
            ic("fail in update button state")

class ConnectionDock(QDockWidget):
    """connect/Login """

    def __init__ (self, mc):
        QDockWidget.__init__(self)

        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)

        # host line
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        # class ID
        self.eClientID = QLineEdit()
        self.eClientID.setText(clientname)

        # self.eUserName = QLineEdit()
        # self.eUserName.setText(username)
        #
        # self.ePassword = QLineEdit()
        # self.ePassword.setEchoMode(QLineEdit.Password)
        # self.ePassword.setText(password)

        self.eConnectbtn = QPushButton("Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: red")

        formLayot = QFormLayout()
        formLayot.addRow("Host", self.eHostInput)
        formLayot.addRow("Class ID", self.eClientID)
        # formLayot.addRow("User Name", self.eUserName)
        # formLayot.addRow("Password", self.ePassword)
        formLayot.addRow("", self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

    def on_connected (self):
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click (self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(broker_port))
        self.mc.set_clientName(clientname)
        self.mc.set_username(username)
        self.mc.set_password(password)
        self.mc.connect_to()
        self.mc.start_listening()

class PublishDock(QDockWidget):
    """Publisher - A click button to control the windows in class."""

    def __init__ (self, mc):
        QDockWidget.__init__(self)
        self.mc = mc

        # Automatic control button
        self.eAutomaticButton = QPushButton("Automatic")
        self.eAutomaticButton.setStyleSheet("background-color:lightgreen")
        self.eAutomaticButton.setCheckable(True)
        self.eAutomaticButton.toggled.connect(self.toggleAutomatic)

        # Button to open or close the windows
        self.eWindowButton = QPushButton("Open Windows")
        self.eWindowButton.clicked.connect(self.toggleWindow)

        # Label to display window status
        self.windowStatusLabel = QLabel("Window Status: Closed")

        layout = QVBoxLayout()
        layout.addWidget(self.eAutomaticButton)
        layout.addWidget(self.eWindowButton)
        layout.addWidget(self.windowStatusLabel)

        widget = QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Window Control")

    def toggleAutomatic(self, checked):
        """Toggle between automatic and manual control."""
        if checked:
            self.eAutomaticButton.setText("Manual")
            self.eAutomaticButton.setStyleSheet("background-color:lightgray")
            IS_AUTO=False
            ic
        else:
            self.eAutomaticButton.setText("Automatic")
            self.eAutomaticButton.setStyleSheet("background-color:lightgreen")
            IS_AUTO = False

    def toggleWindow(self):
        """Toggle between opening and closing windows."""
        if IS_OPEN:
            window_status = "closed"
            IS_OPEN = False
        else:
            window_status = "open"
            IS_OPEN = True
        MainWindow.controlWindows(IS_OPEN)
        self.windowStatusLabel.setText(f"Window Status: {window_status.capitalize()}")

class StatusDock(QDockWidget):
    """Subscriber - Displays subscribed messages and highlights specific values."""

    def __init__ (self, mc):
        QDockWidget.__init__(self)
        self.mc = mc

        self.temperatureLabel = QLabel("Temperature: -")
        self.humidityLabel = QLabel("Humidity: -")
        self.eco2Label = QLabel("eCO2: -")
        self.tvocsLabel = QLabel("TVOCs: -")

        layout = QVBoxLayout()
        layout.addWidget(self.temperatureLabel)
        layout.addWidget(self.humidityLabel)
        layout.addWidget(self.eco2Label)
        layout.addWidget(self.tvocsLabel)

        widget = QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Status")

    def on_mqtt_connected (self):
        print("MQTT Connected")
        self.mc.subscribe_to("DHT_topic")
        self.mc.subscribe_to("AQS_topic")
        self.mc.start_listening()

    def handleMessage (self, topic, payload):
        """Handle incoming messages."""
        message = payload.decode("utf-8", "ignore")

        # Check which sensor the message is from and extract values
        if "DHT_topic" in topic:
            temperature, humidity = map(float, message.split(" "))
            self.updateStatus(self.temperatureLabel, temperature, "Temperature")
            self.updateStatus(self.humidityLabel, humidity, "Humidity")
        elif "AQS_topic" in topic:
            tvocs, eco2 = map(float, message.split(" "))
            self.updateStatus(self.eco2Label, eco2, "eCO2")
            self.updateStatus(self.tvocsLabel, tvocs, "TVOCs")

    def updateStatus (self, label, value, parameter):
        """Update status for a parameter."""
        label.setText(f"{parameter}: {value}")
        if parameter in ("Temperature", "Humidity"):
            if parameter == "Temperature":
                if not (20 <= value <= 30):
                    self.HandleAbnormalValue(label)
                else:
                    self.setStatusNormal(label)
            elif parameter == "Humidity":
                if not (30 <= value <= 60):
                    self.HandleAbnormalValue(label)
                else:
                    self.setStatusNormal(label)
        elif parameter in ("eCO2", "TVOCs"):
            if not (0 <= value <= 300):
                self.HandleAbnormalValue(label)
            else:
                self.setStatusNormal(label)

    def setStatusNormal (self, label):
        """Set status text color to black and normal font."""
        label.setStyleSheet("color: black; font-weight: normal;")

    def HandleAbnormalValue (self, label):
        """Set status text color to red and bold font.
            if defined to auto mode - will open the windows"""
        label.setStyleSheet("color: red; font-weight: bold;")
        if IS_AUTO:
            MainWindow.controlWindows(True)



class MainWindow(QMainWindow):

    def __init__ (self, parent=None):
        QMainWindow.__init__(self, parent)

        # Init of Mqtt_client class
        self.mc = MC()

        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 100, 500, 300)
        self.setWindowTitle('Monitor GUI')

        # Init QDockWidget objects
        self.connectionDock = ConnectionDock(self.mc)
        self.publishDock = PublishDock(self.mc)
        self.StatusDock = StatusDock(self.mc)

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.TopDockWidgetArea, self.publishDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.StatusDock)

    def controlWindows(self, to_open):
        if to_open:
            self.mc.publish_to(relay_topic,"open")
        else:
            self.mc.publish_to(relay_topic, "close")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    app.exec_()
