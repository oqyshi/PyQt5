import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLineEdit, QLabel, QRadioButton, QHBoxLayout, QPushButton, \
    QMessageBox, QComboBox, QFileDialog, QInputDialog
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap
import sqlite3
from shutil import copyfile
import os


class Teacher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 800, 500)
        self.groups = {}
        self.setWindowTitle('Main')

        self.box = QComboBox(self)
        self.box.move(10, 10)
        self.box.currentTextChanged.connect(self.showgroup)

        self.box1 = QComboBox(self)
        self.box1.move(100, 10)
        self.box1.currentTextChanged.connect(self.showfile)

        self.btn = QPushButton('Log Out', self)
        self.btn.move(700, 10)
        self.btn.clicked.connect(self.logoff)

        self.btn1 = QPushButton('Download', self)
        self.btn1.move(450, 10)
        self.btn1.clicked.connect(self.download)

        self.btn2 = QPushButton('Add Document', self)
        self.btn2.resize(self.btn2.sizeHint())
        self.btn2.move(200, 10)
        self.btn2.clicked.connect(self.upload)

        self.btn3 = QPushButton('Delete', self)
        self.btn3.move(350, 10)
        self.btn3.clicked.connect(self.delete)

        self.btn4 = QPushButton('Add Student', self)
        self.btn4.move(570, 10)
        self.btn4.clicked.connect(self.addstudent)

        self.lbl = QLabel(self)
        self.lbl.move(10, 100)

    def news(self):
        con = sqlite3.connect('nov.db')
        cursor = con.cursor()
        self.groupsid = cursor.execute(f'''SELECT Groups FROM Teachers Where id = {USER[0]}''').fetchone()
        if self.groupsid[0]:
            for value, key in cursor.execute(f'''SELECT id, Title FROM Groups Where id
             IN ({self.groupsid[0]})''').fetchall():
                self.groups[key] = value
        con.close()
        self.box.clear()
        self.box.addItems(list(self.groups))

    def showgroup(self):
        self.box1.clear()
        con = sqlite3.connect('nov.db')
        cursor = con.cursor()
        item = None
        if self.box.currentText():
            item = cursor.execute(
                f"""SELECT Files FROM Groups Where id = {self.groups[self.box.currentText()]}""").fetchone()[0]
        con.close()
        if item:
            self.box1.addItems(item.split(','))

    def upload(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать файл', '')[0]
        if fname:
            copyfile(fname, 'files/' + fname.split('/')[-1])
            fname = fname.split('/')[-1]
            con = sqlite3.connect('nov.db')
            cursor = con.cursor()
            item = None
            if self.box.currentText():
                item = cursor.execute(
                    f"""SELECT Files FROM Groups Where id = {self.groups[self.box.currentText()]}""").fetchone()[0]
            zdez = []
            if item:
                zdez = item.split(',')
            if fname not in zdez:
                zdez.append(fname)
            cursor.execute(
                f"""UPDATE Groups SET Files='{','.join(zdez)}' Where id = {self.groups[self.box.currentText()]}""")
            con.commit()
            con.close()
            self.box1.clear()
            self.box1.addItems(zdez)

    def logoff(self):
        TEACHER.hide()
        MAIN.show()

    def download(self):
        if self.box1.currentText():
            fname = QFileDialog.getExistingDirectory(self, 'Выбрать место', '')
            copyfile('files/' + self.box1.currentText(), fname + '/' + self.box1.currentText())
        else:
            QMessageBox.about(self, "Error", 'Chose file')

    def delete(self):
        if self.box1.currentText():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Are you sure you want to delete the file?")
            msg.setWindowTitle("Сonfirmation")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.buttonClicked.connect(self.deleteTrue)
            msg.exec_()
        else:
            QMessageBox.about(self, "Error", 'Chose file')

    def deleteTrue(self, i):
        if i.text() == 'OK':
            con = sqlite3.connect('nov.db')
            cursor = con.cursor()
            item = None
            if self.box.currentText():
                item = cursor.execute(
                    f"""SELECT Files FROM Groups Where id = {self.groups[self.box.currentText()]}""").fetchone()[0]
            zdez = item.split(',')
            zdez.remove(self.box1.currentText())
            cursor.execute(
                f"""UPDATE Groups SET Files='{','.join(zdez)}' Where id = {self.groups[self.box.currentText()]}""")
            con.commit()
            con.close()
            os.remove("files/" + self.box1.currentText())
            self.box1.clear()
            self.box1.addItems(zdez)

    def addstudent(self):
        if self.box.currentText():
            group = self.groups[self.box.currentText()]
            con = sqlite3.connect('nov.db')
            cursor = con.cursor()
            item = cursor.execute(
                f"""SELECT id, Login, Groups FROM Students""").fetchall()

            result, ok = QInputDialog.getItem(self, "Select student to add",
                                            "Students", map(lambda x: x[1], item), 0, False)
            for i in item:
                if i[1] == result:
                    result = i
                    break
            allgroups = []
            if result[2]:
                allgroups = str(result[2]).split(',')

            if ok and (group not in allgroups):
                allgroups.append(group)
                cursor.execute(
                    f"""UPDATE Students SET Groups='{','.join(str(i) for i in allgroups)}' Where id = {result[0]}""")
            con.commit()
            con.close()
        else:
            QMessageBox.about(self, "Error", 'Chose group')

    def showfile(self):
        a = self.box1.currentText()
        if a:
            if 'txt' in a:
                file = 'images/txt.png'
            elif 'pdf' in a:
                file = 'images/pdf.jpeg'
            elif 'ppt' in a:
                file = 'images/ppt.png'
            elif 'doc' in a:
                file = 'images/doc.png'
            elif 'py' in a:
                file = 'images/py.jpeg'
            elif a.split('.')[-1] in ['jpeg', 'png', 'bmp']:
                file = 'files/' + a
            else:
                file = 'images/un.jpg'
            self.pixmap = QPixmap(file)
            self.lbl.resize(250, 250)
            self.lbl.setPixmap(self.pixmap)


class Student(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 600, 400)
        self.fig = 0
        self.setWindowTitle('Main')
        self.groups = {}

        self.btn = QPushButton('Log Out', self)
        self.btn.move(500, 10)
        self.btn.clicked.connect(self.logoff)

        self.btn1 = QPushButton('Download', self)
        self.btn1.move(400, 10)
        self.btn1.clicked.connect(self.download)

        self.box = QComboBox(self)
        self.box.move(10, 10)
        self.box.currentTextChanged.connect(self.showgroup)

        self.box1 = QComboBox(self)
        self.box1.move(100, 10)
        self.box1.currentTextChanged.connect(self.showfile)

        self.lbl = QLabel(self)
        self.lbl.move(10, 100)

    def showgroup(self):
        self.box1.clear()
        con = sqlite3.connect('nov.db')
        cursor = con.cursor()
        item = None
        if self.box.currentText():
            item = cursor.execute(
                f"""SELECT Files FROM Groups Where id = {self.groups[self.box.currentText()]}""").fetchone()[0]
        con.close()
        if item:
            self.box1.addItems(item.split(','))

    def logoff(self):
        STUDENT.hide()
        MAIN.show()

    def news(self):
        con = sqlite3.connect('nov.db')
        cursor = con.cursor()
        self.groupsid = cursor.execute(f'''SELECT Groups FROM Students Where id = {USER[0]}''').fetchone()
        if self.groupsid[0]:
            for value, key in cursor.execute(f'''SELECT id, Title FROM Groups Where id
             IN ({self.groupsid[0]})''').fetchall():
                self.groups[key] = value
        con.close()
        self.box.clear()
        self.box.addItems(list(self.groups))

    def download(self):
        if self.box1.currentText():
            fname = QFileDialog.getExistingDirectory(self, 'Выбрать место', '')
            copyfile('files/' + self.box1.currentText(), fname + '/' + self.box1.currentText())
        else:
            QMessageBox.about(self, "Error", 'Chose file')

    def showfile(self):
        a = self.box1.currentText()
        if a:
            if 'txt' in a:
                file = 'images/txt.png'
            elif 'pdf' in a:
                file = 'images/pdf.jpeg'
            elif 'ppt' in a:
                file = 'images/ppt.png'
            elif 'doc' in a:
                file = 'images/doc.png'
            elif 'py' in a:
                file = 'images/py.jpeg'
            elif a.split('.')[-1] in ['jpeg', 'png', 'bmp']:
                file = 'files/' + a
            else:
                file = 'images/un.jpg'
            self.pixmap = QPixmap(file)
            self.lbl.resize(250, 250)
            self.lbl.setPixmap(self.pixmap)


class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 350, 400)
        self.setWindowTitle('Login')

        self.logintitle = QLabel('Login', self)
        self.logintitle.move(50, 20)

        self.login = QLineEdit(self)
        self.login.move(50, 70)

        self.passwordtitle = QLabel('Password', self)
        self.passwordtitle.move(50, 120)

        self.password = QLineEdit(self)
        self.password.move(50, 170)

        self.roletitle = QLabel('Role', self)
        self.roletitle.move(50, 220)

        self.horizontalLayoutWidget = QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(50, 250, 300, 50))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.radioButton_1 = QRadioButton('Teacher', self.horizontalLayoutWidget)
        self.radioButton_2 = QRadioButton('Student', self.horizontalLayoutWidget)
        self.horizontalLayout.addWidget(self.radioButton_1)
        self.horizontalLayout.addWidget(self.radioButton_2)

        self.btn = QPushButton('Login', self)
        self.btn.move(50, 320)
        self.btn.clicked.connect(self.log)

    def log(self):
        if self.radioButton_1.isChecked():
            con = sqlite3.connect('nov.db')
            cursor = con.cursor()
            item = cursor.execute(
                f"""SELECT Login, Pass, id FROM Teachers Where Login = '{self.login.text()}'""").fetchone()
            con.close()
            if item:
                if self.password.text() == str(item[1]):
                    USER[0] = item[2]
                    TEACHER.show()
                    TEACHER.news()
                    MAIN.hide()
                else:
                    QMessageBox.about(self, "Error", 'Wrong password')
            else:
                QMessageBox.about(self, "Error", 'There is no such user')
        elif self.radioButton_2.isChecked():
            con = sqlite3.connect('nov.db')
            cursor = con.cursor()
            item = cursor.execute(
                f"""SELECT Login, Pass, id FROM Students Where Login = '{self.login.text()}'""").fetchone()
            con.close()
            if item:
                if self.password.text() == str(item[1]):
                    USER[0] = item[2]
                    STUDENT.show()
                    STUDENT.news()
                    MAIN.hide()
                else:
                    QMessageBox.about(self, "Error", 'Wrong password')
            else:
                QMessageBox.about(self, "Error", 'There is no such user')

        else:
            QMessageBox.about(self, "Error", "Chose role")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    USER = [0]
    STUDENT = Student()
    TEACHER = Teacher()
    MAIN = Login()
    MAIN.show()
    sys.exit(app.exec_())
