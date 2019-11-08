import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLineEdit, QLabel, QRadioButton, QHBoxLayout, QPushButton, \
    QMessageBox, QComboBox, QFileDialog, QInputDialog
from PyQt5 import QtCore
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
        self.box.setToolTip('Choose which group to manage')

        self.box1 = QComboBox(self)
        self.box1.move(100, 10)
        self.box1.currentTextChanged.connect(self.showfile)
        self.box1.setToolTip('Choose which file to manage')

        self.btn = QPushButton('Log Out', self)
        self.btn.move(700, 60)
        self.btn.clicked.connect(self.logoff)
        self.btn.setToolTip('Log out and move to login screen')

        self.btn1 = QPushButton('Download', self)
        self.btn1.move(450, 10)
        self.btn1.clicked.connect(self.download)
        self.btn1.setToolTip('Download chosed file to computer')
        self.btn1.resize(self.btn1.sizeHint())

        self.btn2 = QPushButton('Add Document', self)
        self.btn2.resize(self.btn2.sizeHint())
        self.btn2.move(200, 10)
        self.btn2.clicked.connect(self.upload)
        self.btn2.setToolTip('Add Document to chosen group from computer')

        self.btn3 = QPushButton('Delete', self)
        self.btn3.move(350, 10)
        self.btn3.clicked.connect(self.delete)
        self.btn3.setToolTip('Delete chosen file from group')
        self.btn3.resize(self.btn3.sizeHint())

        self.btn4 = QPushButton('Add Student', self)
        self.btn4.move(570, 10)
        self.btn4.clicked.connect(self.addstudent)
        self.btn4.resize(self.btn4.sizeHint())
        self.btn4.setToolTip('Chose student and add to group')

        self.btn5 = QPushButton('Create Group', self)
        self.btn5.move(570, 60)
        self.btn5.clicked.connect(self.createGroup)
        self.btn5.resize(self.btn5.sizeHint())
        self.btn5.setToolTip('Chose student and add to group')

        self.lbl = QLabel(self)
        self.lbl.move(10, 100)

        self.lbl2 = QLabel(self)
        self.lbl2.move(700, 10)

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

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == 16777219:
            self.delete()
        elif QKeyEvent.key() == 68:
            self.download()
        elif QKeyEvent.key() == 85:
            self.upload()
        elif QKeyEvent.key() == 16777216:
            self.close()
        elif QKeyEvent.key() == 67:
            self.createGroup()

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
            files = []
            if item:
                files = item.split(',')
            if fname not in files:
                files.append(fname)
            cursor.execute(
                f"""UPDATE Groups SET Files='{','.join(files)}' Where id = {self.groups[self.box.currentText()]}""")
            con.commit()
            con.close()
            self.box1.clear()
            self.box1.addItems(files)
        else:
            QMessageBox.about(self, "Succes", "File wasn't added")

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
            files = item.split(',')
            files.remove(self.box1.currentText())
            cursor.execute(
                f"""UPDATE Groups SET Files='{','.join(files)}' Where id = {self.groups[self.box.currentText()]}""")
            con.commit()
            con.close()
            os.remove("files/" + self.box1.currentText())
            self.box1.clear()
            self.box1.addItems(files)
            QMessageBox.about(self, "Succes", 'File was deleted')
        else:
            QMessageBox.about(self, "Succes", "File wasn't deleted")

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
                QMessageBox.about(self, "Succes", 'Student added')
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
            self.pixmap = QPixmap(file).scaled(250, 250)
            self.lbl.resize(250, 250)
            self.lbl.setPixmap(self.pixmap)

    def createGroup(self):
        text, ok = QInputDialog.getText(self, 'Input name of group', 'Name')
        if ok:
            con = sqlite3.connect('nov.db')
            cursor = con.cursor()
            item = None
            if text:
                if text not in list(
                        map(lambda x: x[0], cursor.execute(f"""SELECT Title FROM Groups""").fetchall())):
                    cursor.execute(
                        f"""INSERT INTO Groups(Title, Files) VALUES ('{text}', '') """)
                    newid = cursor.execute(
                        f"""SELECT id FROM Groups Where title='{text}' """).fetchone()[0]
                    groupsid = []
                    item = cursor.execute(f'''SELECT Groups FROM Teachers Where id = {USER[0]}''').fetchone()[
                        0]
                    if item:
                        groupsid = item.split(',')
                    groupsid.append(str(newid))
                    cursor.execute(
                        f"""UPDATE Teachers SET Groups='{','.join(groupsid)}' Where id = {USER[0]} """)
                    self.box.clear()

                    QMessageBox.about(self, "Succes", 'Group created')
                else:
                    QMessageBox.about(self, "Error", 'There is already existing group with this name')
            else:
                QMessageBox.about(self, "Error", 'Write name of group')
            con.commit()
            con.close()
            self.news()


class Student(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Main')
        self.groups = {}

        self.btn = QPushButton('Log Out', self)
        self.btn.move(500, 60)
        self.btn.clicked.connect(self.logoff)
        self.btn.setToolTip('Log out and move to login screen')

        self.btn1 = QPushButton('Download', self)
        self.btn1.move(400, 10)
        self.btn1.clicked.connect(self.download)
        self.btn1.setToolTip('Download chosed file to computer')

        self.box = QComboBox(self)
        self.box.move(10, 10)
        self.box.currentTextChanged.connect(self.showgroup)
        self.box.setToolTip('Chose which group to follow')

        self.box1 = QComboBox(self)
        self.box1.move(100, 10)
        self.box1.currentTextChanged.connect(self.showfile)
        self.box1.setToolTip('Chose which file to follow')

        self.lbl = QLabel(self)
        self.lbl.move(10, 100)

        self.lbl2 = QLabel(self)
        self.lbl2.move(500, 10)

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
            QMessageBox.about(self, "Succes", 'File added to folder')
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

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == 68:
            self.download()
        elif QKeyEvent.key() == 16777216:
            self.close()


class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 350, 450)
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

        self.btn1 = QPushButton('Create account', self)
        self.btn1.move(50, 370)
        self.btn1.clicked.connect(self.reg)

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

    def reg(self):
        REG.show()
        MAIN.hide()


class Registration(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 350, 500)
        self.setWindowTitle('Registration')

        self.logintitle = QLabel('Login', self)
        self.logintitle.move(50, 20)

        self.login = QLineEdit(self)
        self.login.move(50, 70)

        self.passwordtitle = QLabel('Password', self)
        self.passwordtitle.move(50, 120)

        self.passwordtitle1 = QLabel('Repeat password', self)
        self.passwordtitle1.move(50, 220)

        self.password = QLineEdit(self)
        self.password.move(50, 170)

        self.password1 = QLineEdit(self)
        self.password1.move(50, 270)

        self.roletitle = QLabel('Role', self)
        self.roletitle.move(50, 320)

        self.horizontalLayoutWidget = QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(50, 350, 300, 50))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.radioButton_1 = QRadioButton('Teacher', self.horizontalLayoutWidget)
        self.radioButton_2 = QRadioButton('Student', self.horizontalLayoutWidget)
        self.horizontalLayout.addWidget(self.radioButton_1)
        self.horizontalLayout.addWidget(self.radioButton_2)

        self.btn = QPushButton('Register', self)
        self.btn.move(50, 420)
        self.btn.clicked.connect(self.register)

        self.btn1 = QPushButton('I already have account', self)
        self.btn1.move(50, 470)
        self.btn1.clicked.connect(self.log)

    def register(self):
        if self.radioButton_1.isChecked():
            con = sqlite3.connect('nov.db')
            cursor = con.cursor()
            names = list(map(lambda x: x[0], cursor.execute(
                f"""SELECT Login FROM Teachers""").fetchall()))
            if self.login.text() and self.login.text() not in names:
                if self.password1.text() == self.password.text() and self.password.text():
                    cursor.execute(
                        f"""INSERT INTO Teachers(Login, Pass) VALUES ('{self.login.text()}','{self.password.text()}')""")
                    con.commit()
                    con.close()
                    MAIN.show()
                    REG.hide()
                else:
                    QMessageBox.about(self, "Error", "Wrong passwords format")
            else:
                QMessageBox.about(self, "Error", "This login is inappropriate")

        elif self.radioButton_2.isChecked():
            con = sqlite3.connect('nov.db')
            cursor = con.cursor()
            names = list(map(lambda x: x[0], cursor.execute(
                f"""SELECT Login FROM Students""").fetchall()))
            if self.login.text() and self.login.text() not in names:
                print(self.password.text(), self.password.text())
                if self.password1.text() == self.password.text() and self.password.text():
                    cursor.execute(
                        f"""INSERT INTO Students(Login, Pass) VALUES ('{self.login.text()}','{self.password.text()}')""")
                    con.commit()
                    con.close()
                    MAIN.show()
                    REG.hide()
                else:
                    QMessageBox.about(self, "Error", "Wrong passwords format")
            else:
                QMessageBox.about(self, "Error", "This login is inappropriate")

        else:
            QMessageBox.about(self, "Error", "Chose role")

    def log(self):
        MAIN.show()
        REG.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    USER = [0]
    STUDENT = Student()
    TEACHER = Teacher()
    REG = Registration()
    MAIN = Login()
    MAIN.show()
    sys.exit(app.exec_())
