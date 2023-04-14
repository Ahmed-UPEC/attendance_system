import os, sys, math, pdb

import mysql.connector 

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QWidget
from PyQt5.uic import loadUi

from gui import Ui_MainWindow
from dashboard import Ui_Dashboard

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="attendance"
)

mycursor = mydb.cursor()

class MyMainWindow(QMainWindow, Ui_MainWindow) :
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.submit.clicked.connect(self.onSubmit)
        
    def onSubmit(self):
        # check if the user exists in the database
        # if yes, then check if the password is correct
        # if yes, then open the main window
        
        check = self.checkUser(self.ui.username.text(), self.ui.password.text())
        if check:
            self.openMainWindow()
        else:
            self.showMessageBox("Error", "Username or Password is incorrect")
    
    def checkUser(self, username, password):
        sql = "SELECT * FROM accounts WHERE name = %s AND password = %s"
        val = (username, password)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            print("User does not exist")
            return False
        else:
            print("Username or Password is incorrect")
            return True

    """
    Open the main window
    """
    def openMainWindow(self):
        print("Open the main window")
        self.ui.username.setText("")
        self.ui.password.setText("")
        # self.showMessageBox("Success", "User exists")
        # open dashboard window
        self.dashboard = QtWidgets.QMainWindow()
        self.dasboardUi = Ui_Dashboard()
        self.dasboardUi.setupUi(self.dashboard)
        self.dasboardUi.student_selector.currentIndexChanged.connect(self.updateDashboardTable)
        self.dashboard.show()
        self.addStudentToDashboardComboBox()

    """
    Show a message box
    """
    def showMessageBox(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_()

    """
    Add student to combobox in dashboard using the attendance table
    the sql query should extract only the student names from the attendance table without duplicates
    """
    def addStudentToDashboardComboBox(self):
        sql = "SELECT DISTINCT name FROM attendance"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x)
            self.dasboardUi.student_selector.addItem(x[0])
        self.updateDashboardTable()
        
    
    """
    Update the dashboard table with the attendance of the selected student
    """
    def updateDashboardTable(self):
        # get the student name from the combobox
        student_name = self.dasboardUi.student_selector.currentText()
        # get the attendance of the student from the attendance table without its id
        sql = "SELECT name, timestamp FROM attendance WHERE name = %s"
        val = (student_name,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        # add the attendance to the table
        self.dasboardUi.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(myresult):
            self.dasboardUi.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.dasboardUi.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

        self.updateTotalAttendance(myresult)

    """
    Update the total attendance of the selected student
    """
    def updateTotalAttendance(self, myresult) :
        self.dasboardUi.tot_attendance.setText("Total attendance : " + str(len(myresult)))
        


    
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())