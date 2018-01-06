import sys
import random
import pickle

import matplotlib
import itertools
from PyQt5.QtCore import Qt, pyqtSignal, QObject

matplotlib.use("Qt5Agg")
import mpl_toolkits.mplot3d
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QGraphicsView, QGraphicsScene, QVBoxLayout, QGridLayout, \
    QSizePolicy, QMessageBox, QWidget, QDesktopWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QComboBox, QFileDialog
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# 对浮点数进行“精确”运算
from decimal import *

FrontView = 0
SideView = 1
VerticalView = 2

DashLine = 0
SolidLine = 1


class Communicate(QObject):
    signal = pyqtSignal()


class Messenger():
    def __init__(self):
        self.setupFlag = False

    def setup(self, statusBar, viewData):
        self.statusBar = statusBar
        self.viewData = viewData
        # self.vPaint = Communicate()
        # self.vPaint.signal.connect(self.v.paintEvent)
        # self.v1Paint = Communicate()
        # self.v1Paint.signal.connect(self.v1.paintEvent)
        # self.v2Paint = Communicate()
        # self.v2Paint.signal.connect(self.v2.paintEvent)
        # self.v3Paint = Communicate()
        # self.v3Paint.signal.connect(self.v3.paintEvent)
        self.setupFlag = True

    def changeStatusBar(self, content):
        try:
            if self.setupFlag:
                self.statusBar.showMessage(content)
                if content.startswith('press at view'):
                    index = int(content[15:16])
                    aw.viewComboBox.setCurrentIndex(index)
                elif content.startswith('press at Main View'):
                    aw.viewComboBox.setCurrentIndex(3)
                elif content.startswith('press at point'):
                    v, index = content[16:18]
                    viewTypes = {'A': FrontView, 'B': SideView, 'C': VerticalView}
                    index = int(index)
                    aw.viewComboBox.setCurrentIndex(viewTypes[v])
                    x = self.viewData.Point[viewTypes[v]]['x'][index]
                    y = self.viewData.Point[viewTypes[v]]['y'][index]
                    z = self.viewData.Point[viewTypes[v]]['z'][index]
                    aw.dataLineEdits[0].setText(content[16:18])
                    aw.dataLineEdits[1].setText(str(x))
                    aw.dataLineEdits[2].setText(str(y))
                    aw.dataLineEdits[3].setText(str(z))
                elif content.startswith('release event at point'):
                    v, index = content[24:26]
                    viewTypes = {'A': FrontView, 'B': SideView, 'C': VerticalView}
                    index = int(index)
                    aw.viewComboBox.setCurrentIndex(viewTypes[v])
                    x = self.viewData.Point[viewTypes[v]]['x'][index]
                    y = self.viewData.Point[viewTypes[v]]['y'][index]
                    z = self.viewData.Point[viewTypes[v]]['z'][index]
                    aw.dataLineEdits[0].setText(content[24:26])
                    aw.dataLineEdits[1].setText(str(x))
                    aw.dataLineEdits[2].setText(str(y))
                    aw.dataLineEdits[3].setText(str(z))
                else:
                    pass
        except Exception as e:
            print(e)

    def changeViewDataByPoint(self, viewType, index, x, y, z, operation='modify'):
        if self.setupFlag:
            if operation == 'modify':
                viewData.Point[viewType]['x'][index] = float(x)
                viewData.Point[viewType]['y'][index] = float(y)
                viewData.Point[viewType]['z'][index] = float(z)
                vpMainView.viewData.Point[viewType]['x'][index] = float(x)
                vpMainView.viewData.Point[viewType]['y'][index] = float(y)
                vpMainView.viewData.Point[viewType]['z'][index] = float(z)
            elif operation == 'add':
                viewData.addPoint(view=viewType, x=x, y=y, z=z)
                i = len(aw.vpViews[viewType].buttons)
                b = PointButton(chr(65 + viewType) + str(i))
                b.setToolTip('')
                b.resize(10, 10)
                b.move(100, 100)
                b.setParent(aw.vpViews[viewType])
                b.show()
                aw.vpViews[viewType].buttons.append(b)
                # vpMainView.viewData.addPoint(view=viewType, x=x, y=y, z=z)
            elif operation == 'delete':
                viewData.deletePoint(view=viewType, index=index)
                aw.vpViews[viewType].buttons[index].deleteLater()
                aw.vpViews[viewType].buttons.pop(index)
                # 调整按钮的access name
                for i in range(index, len(aw.vpViews[viewType].buttons)):
                    aw.vpViews[viewType].buttons[i].setAccessibleName(str(i))
                    aw.vpViews[viewType].buttons[i].setText(chr(65 + viewType) + str(i))

            vpFrontView.repaint()
            vpSideView.repaint()
            vpVerticalView.repaint()
            # self.v1Paint.signal.emit()
            # self.v2Paint.signal.emit()
            # self.v3Paint.signal.emit()

    def changeViewDataByLine(self, viewType, operation, a, b):
        if self.setupFlag:
            if operation == 'add':
                viewData.addLine(view=viewType, s=a, e=b)
                # vpMainView.viewData.addLine(view=viewType, s=a, e=b)
            elif operation == 'delete':
                viewData.deleteLine(view=viewType, s=a, e=b)
                # vpMainView.viewData.deleteLine(view=viewType, s=a, e=b)

            vpFrontView.repaint()
            vpSideView.repaint()
            vpVerticalView.repaint()

    def buttonClicked(self, index):
        index = int(index)
        viewType = int(aw.viewComboBox.currentIndex())
        # 点：新增，修改，删除
        if index < 3:
            try:
                x = float(aw.dataLineEdits[1].text())
                y = float(aw.dataLineEdits[2].text())
                z = float(aw.dataLineEdits[3].text())
            except Exception as e:
                reply = QMessageBox.information(aw, '错误', '请补充完整的点坐标!')
                return
            try:
                v, i = aw.dataLineEdits[0].text()
                i = int(i)
            except Exception as e:
                print(e)
            # 点：新增
            if index == 0 and viewType < 3:
                self.changeViewDataByPoint(viewType=viewType, operation='add', index=None, x=x, y=y, z=z)
            # 点：修改
            if index == 1 and viewType < 3:
                self.changeViewDataByPoint(viewType=viewType, index=i, x=x, y=y, z=z)
            # 点：删除
            if index == 2 and viewType < 3:
                try:
                    v, i = aw.dataLineEdits[0].text()
                    i = int(i)
                except Exception as e:
                    reply = QMessageBox.information(aw, '错误', '请补充完整点名称!')
                self.changeViewDataByPoint(viewType=viewType, operation='delete', index=i, x=x, y=y, z=z)
        # 线段：新增
        elif index == 3 and viewType <  3:
            try:
                v1, i1 = aw.dataLineEdits[4].text()
                v2, i2 = aw.dataLineEdits[5].text()
            except Exception as e:
                print(e)
                reply = QMessageBox.information(aw, '错误', '请补充完整的端点名称!')
                return
            i1 = int(i1)
            i2 = int(i2)
            length = len(aw.vpMainView.viewData.Point[viewType]['x'])
            if v1 == v2 and v1 == chr(viewType + 65) and i1 in range(length) and i2 in range(length):
                if aw.vpMainView.viewData.lineExist(view=viewType, index1=i1, index2=i2):
                    reply = QMessageBox.information(aw, '错误', '新增线段已存在!')
                    return
                self.changeViewDataByLine(viewType=viewType, operation='add', a=i1, b=i2)
            else:
                reply = QMessageBox.information(aw, '错误', '请补充完整的端点名称!')
        # 线段：删除
        elif index == 4 and viewType < 3:
            try:
                v1, i1 = aw.dataLineEdits[4].text()
                v2, i2 = aw.dataLineEdits[5].text()
            except Exception as e:
                print(e)
                reply = QMessageBox.information(aw, '错误', '请补充完整的端点名称!')
                return
            i1 = int(i1)
            i2 = int(i2)
            length = len(aw.vpMainView.viewData.Point[viewType]['x'])
            if v1 == v2 and v1 == chr(viewType + 65) and i1 in range(length) and i2 in range(length):
                if not aw.vpMainView.viewData.lineExist(view=viewType, index1=i1, index2=i2):
                    reply = QMessageBox.information(aw, '错误', '删除线段不存在!')
                    return
                self.changeViewDataByLine(viewType=viewType, operation='delete', a=i1, b=i2)
            else:
                reply = QMessageBox.information(aw, '错误', '请补充完整的端点名称!')
        # 面积：查询
        elif index == 5:
            a = ord(aw.dataLineEdits[6].text()) - 65
            b = ord(aw.dataLineEdits[7].text()) - 65
            c = ord(aw.dataLineEdits[8].text()) - 65

            if aw.vpMainView.certainPlane.count({a, b, c}) > 0:
                i = aw.vpMainView.certainPlane.index({a, b, c})
                aw.areaLabel.setText(str(round(aw.vpMainView.areaForPlane[i], 3)))
            else:
                reply = QMessageBox.information(aw, '错误', '指定面不存在!')
                aw.areaLabel.setText('')
        elif index == 6:
            self.verifyData()
        elif index == 7:
            self.generateModel()
        elif index == 8:
            self.reportMessage()
        # 线段：查询长度
        elif index == 9:
            if viewType == 3:
                a = ord(aw.dataLineEdits[4].text()) - 65
                b = ord(aw.dataLineEdits[5].text()) - 65

                if aw.vpMainView.certainLines.count({a, b}) > 0:
                    x1, y1, z1 = aw.vpMainView.certainPoints[a]
                    x2, y2, z2 = aw.vpMainView.certainPoints[b]
                    length = np.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2) + pow(z1 -z2, 2))
                    aw.lengthLabel.setText(str(round(length, 3)))
                else:
                    reply = QMessageBox.information(aw, '错误', '指定线段不存在!')
                    aw.lengthLabel.setText('')
            else:
                try:
                    v1, i1 = aw.dataLineEdits[4].text()
                    v2, i2 = aw.dataLineEdits[5].text()
                    i1 = int(i1)
                    i2 = int(i2)
                except Exception as e:
                    print(e)
                    reply = QMessageBox.information(aw, '错误', '请补充完整的端点名称!')
                    return
                length = len(aw.vpMainView.viewData.Point[viewType]['x'])
                # 允许未连接线段查询
                if v1 == v2 and v1 == chr(viewType + 65) and i1 in range(length) and i2 in range(length):
                    x1 = aw.vpMainView.viewData.Point[viewType]['x'][i1]
                    y1 = aw.vpMainView.viewData.Point[viewType]['y'][i1]
                    z1 = aw.vpMainView.viewData.Point[viewType]['z'][i1]
                    x2 = aw.vpMainView.viewData.Point[viewType]['x'][i2]
                    y2 = aw.vpMainView.viewData.Point[viewType]['y'][i2]
                    z2 = aw.vpMainView.viewData.Point[viewType]['z'][i2]
                    length = np.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2) + pow(z1 - z2, 2))
                    aw.lengthLabel.setText(str(round(length, 3)))
                else:
                    reply = QMessageBox.information(aw, '错误', '指定线段不存在!')
                    aw.lengthLabel.setText('')

    def viewChanged(self):
        # print(aw.viewComboBox.currentText())
        index = aw.viewComboBox.currentIndex()
        for i in range(len(aw.dataLineEdits) - 3):
            aw.dataLineEdits[i].setText('')
        aw.dataLineEdits[1].setEnabled(True)
        aw.dataLineEdits[2].setEnabled(True)
        aw.dataLineEdits[3].setEnabled(True)
        aw.lengthLabel.setText('')
        # aw.buttons[8].setEnabled(False)
        # aw.buttons[9].setEnabled(False)
        if index == 0:
            aw.dataLineEdits[1].setEnabled(False)
            aw.dataLineEdits[1].setText('0.0')
        elif index == 1:
            aw.dataLineEdits[2].setEnabled(False)
            aw.dataLineEdits[2].setText('0.0')
        elif index == 2:
            aw.dataLineEdits[3].setEnabled(False)
            aw.dataLineEdits[3].setText('0.0')
        else:
            pass
        pass

    def verifyData(self):
        message = 'verify data...'
        self.changeStatusBar(message)
        aw.vpMainView.verifyData()
        # print(message)
        pass

    def generateModel(self):
        message = 'generate model...'
        self.changeStatusBar(message)
        aw.vpMainView.computeInitialFigure()
        self.updateInfo()
        # print(message)
        pass

    def reportMessage(self):
        message = 'reporting...'
        self.changeStatusBar(message)
        print(message)
        reportMessage = '几何体统计信息如下：\n' \
                        '点：\n'

        for i in range(len(aw.vpMainView.certainPoints)):
            reportMessage += (chr(65 + i) + ': ' + str(aw.vpMainView.certainPoints[i]) + '\n')
        reportMessage += '\n线：\n'

        for i in range(len(aw.vpMainView.certainLines)):
            a, b = aw.vpMainView.certainLines[i]
            reportMessage += (chr(65 + a) + '-' + chr(65 + b) + ': ' + str(aw.vpMainView.lengthForLine[i]) + '\n')
        reportMessage += '\n面：\n'

        for i in range(len(aw.vpMainView.certainPlane)):
            area = aw.vpMainView.areaForPlane[i]
            a, b, c = aw.vpMainView.certainPlane[i]
            reportMessage += (chr(65 + a) + chr(65 + b) + chr(65 + c) + ': ' + str(area) + '\n')

        reportMessage += '\n表面积：'+ str(aw.vpMainView.areaSum) + '\n'
        reply = QMessageBox.information(aw, 'Report', reportMessage)

    def updateInfo(self):
        aw.pointNumLabel.setText(str(len(aw.vpMainView.certainPoints)))
        aw.lineNumLabel.setText(str(len(aw.vpMainView.certainLines)))
        aw.areaNumLabel.setText(str(len(aw.vpMainView.certainPlane)))

messenger = Messenger()


class ViewData():
    # FrontView = 0
    # SideView = 1
    # VerticalView = 2
    Point = {FrontView: {'x': [], 'y': [], 'z': []},
             SideView: {'x': [], 'y': [], 'z': []},
             VerticalView: {'x': [], 'y': [], 'z': []}}

    Line = {FrontView: {'s': [], 'e': [], 'real': []},
            SideView: {'s': [], 'e': [], 'real': []},
            VerticalView: {'s': [], 'e': [], 'real': []}}

    def __init__(self):
        self.initialize()

    def addPoint(self, view=FrontView, x=0.0, y=0.0, z=0.0):
        self.Point[view]['x'].append(float(x))
        self.Point[view]['y'].append(float(y))
        self.Point[view]['z'].append(float(z))

    def deletePoint(self, view=FrontView, index=0):
        self.Point[view]['x'].pop(index)
        self.Point[view]['y'].pop(index)
        self.Point[view]['z'].pop(index)
        # 调整线段数据,该点以后的点下标减一
        i = 0
        while i < len(self.Line[view]['s']):
            # print(self.Line[view]['s'][i])
            # print(self.Line[view]['e'][i])
            # try:
            #
            #     print(self.Line[view]['s'][i] == index)
            # except Exception as e:
            #     print(e)
            if self.Line[view]['s'][i] == index or self.Line[view]['e'][i] == index:
                self.Line[view]['s'].pop(i)
                self.Line[view]['e'].pop(i)
                self.Line[view]['real'].pop(i)
                i -= 1
            else:
                if self.Line[view]['s'][i] > index:
                    self.Line[view]['s'][i] -= 1
                if self.Line[view]['e'][i] > index:
                    self.Line[view]['e'][i] -= 1

            i += 1

    def addLine(self, view=FrontView, s=0, e=1, real=SolidLine):
        self.Line[view]['s'].append(s)
        self.Line[view]['e'].append(e)
        self.Line[view]['real'].append(real)

    def deleteLine(self, view=FrontView, s=0, e=1):
        index = self.getLineIndex(view=view, s=s, e=e)
        self.Line[view]['s'].pop(index)
        self.Line[view]['e'].pop(index)
        self.Line[view]['real'].pop(index)

    def getLineIndex(self, view=FrontView, s=0, e=0, loop=True):
        sLength = self.Line[view]['s'].count(s)
        lastIndex = -1
        for i in range(sLength):
            index = self.Line[view]['s'].index(s, lastIndex + 1)
            # 投影与数据中线段定义一致
            if e == self.Line[view]['e'][index]:
                return index
            lastIndex = index

        if loop:
            return self.getLineIndex(view=view, s=s, e=e, loop=False)
        return -1

    def getPoint(self, view=FrontView, index=0):
        x = self.Point[view]['x'][index]
        y = self.Point[view]['y'][index]
        z = self.Point[view]['z'][index]
        return [x, y, z]

    def getPointIndex(self, view=FrontView, x=0.0, y=0.0, z=0.0):
        if view is FrontView:
            yLength = self.Point[view]['y'].count(y)
            lastIndex = -1
            for iy in range(yLength):
                lastIndex = self.Point[view]['y'].index(y, lastIndex + 1)
                if self.Point[view]['z'][lastIndex] == z:
                    return lastIndex
        elif view is SideView:
            xLength = self.Point[view]['x'].count(x)
            lastIndex = -1
            for ix in range(xLength):
                lastIndex = self.Point[view]['x'].index(x, lastIndex + 1)
                if self.Point[view]['z'][lastIndex] == z:
                    return lastIndex
        elif view is VerticalView:
            xLength = self.Point[view]['x'].count(x)
            lastIndex = -1
            for ix in range(xLength):
                lastIndex = self.Point[view]['x'].index(x, lastIndex + 1)
                if self.Point[view]['y'][lastIndex] == y:
                    return lastIndex
        else:
            return -1

        print(self.Point[view])
        print('getPointIndex: ', view, x, y, z)
        return -1

    def countTriangleArea(self, a, b, c):
        area = 0

        side = [0, 0, 0]  # 存储三条边的长度;

        side[0] = np.math.sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2) + pow(a[2] - b[2], 2))
        side[1] = np.math.sqrt(pow(a[0] - c[0], 2) + pow(a[1] - c[1], 2) + pow(a[2] - c[2], 2))
        side[2] = np.math.sqrt(pow(c[0] - b[0], 2) + pow(c[1] - b[1], 2) + pow(c[2] - b[2], 2))
        print('side: ', side)
        # 不能构成三角形;
        if side[0] + side[1] <= side[2] or side[0] + side[2] <= side[1] or side[1] + side[2] <= side[0]:
            return area

        # 利用海伦公式。s = sqr(p * (p - a)(p - b)(p - c));
        p = (side[0] + side[1] + side[2]) / 2  # 半周长
        area = np.math.sqrt(p * (p - side[0]) * (p - side[1]) * (p - side[2]))

        return area

    def lineExist(self, view=FrontView, index1=0, index2=1, loop=True):
        # if view==0 and index1==1 and index2==2:
        #     print('here')
        # 如果index1 == index2，即在视图中为同一点，可以相连
        if index1 == index2:
            return True
        # 这里规定，viewData数据中如果视图存在一边可以划分为多条边，只记录最长边
        # 因此需要判断遍历所有边是否重合
        sLength = len(self.Line[view]['s'])
        for i in range(sLength):
            index = i
            # 投影与数据中线段定义一致
            if index1 == self.Line[view]['s'][index] and index2 == self.Line[view]['e'][index]:
                return True
            # 投影是数据中线段的一部分
            else:
                x1, y1, z1 = self.getPoint(view, index1)
                x2, y2, z2 = self.getPoint(view, index2)
                xs, ys, zs = self.getPoint(view, self.Line[view]['s'][index])
                xe, ye, ze = self.getPoint(view, self.Line[view]['e'][index])
                flag = False
                if view is FrontView:
                    x1 = z1
                    x2 = z2
                    xs = zs
                    xe = ze
                elif view is SideView:
                    y1 = z1
                    y2 = z2
                    ys = zs
                    ye = ze
                elif view is VerticalView:
                    pass
                else:
                    return False
                if ys - ye == 0 and xs - xe == 0:
                    flag = (ys == y1 and xs == x1 and ys == y2 and xs == x2)
                elif ys - ye == 0:
                    flag = (ys == y1 and ys == y2
                            and x1 <= max(xs, xe) and x1 >= min(xs, xe)
                            and x2 == max(xs, xe) and x2 >= min(xs, xe))
                elif xs - xe == 0:
                    flag = (xs == x1 and xs == x2
                            and y1 <= max(ys, ye) and y1 >= min(ys, ye)
                            and y2 <= max(ys, ye) and y2 >= min(ys, ye))
                else:
                    flag = ((y2 - y1) * (xs - xe) == (ys - ye) * (x2 - x1)
                            and y1 == ((x1 - xe) / (xs - xe) * (ys - ye) + ye)
                            and y1 <= max(ys, ye) and y1 >= min(ys, ye)
                            and y2 <= max(ys, ye) and y2 >= min(ys, ye))

                if flag:
                    return True

            lastIndex = index
        # sLength = self.Line[view]['s'].count(index1)
        # lastIndex = -1
        # for i in range(sLength):
        #     index = self.Line[view]['s'].index(index1, lastIndex + 1)
        #     # 投影与数据中线段定义一致
        #     if index2 == self.Line[view]['e'][index]:
        #         return True
        #     lastIndex = index

        if loop:
            return self.lineExist(view=view, index1=index2, index2=index1, loop=False)

        return False

    def initialize(self):
        # self.initCube()
        # FrontView
        self.addPoint(FrontView, y=0, z=0)
        self.addPoint(FrontView, y=1, z=0)
        self.addPoint(FrontView, y=0, z=0.5)
        self.addPoint(FrontView, y=1, z=1)
        self.addLine(FrontView, 0, 1, SolidLine)
        self.addLine(FrontView, 1, 3, SolidLine)
        self.addLine(FrontView, 2, 3, SolidLine)
        self.addLine(FrontView, 2, 0, SolidLine)
        self.addLine(FrontView, 3, 0, SolidLine)

        # SideView
        self.addPoint(SideView, x=0, z=0)
        self.addPoint(SideView, x=1, z=0)
        self.addPoint(SideView, x=0, z=1)
        self.addPoint(SideView, x=0, z=0.5)
        self.addLine(SideView, 0, 1, SolidLine)
        self.addLine(SideView, 1, 3, SolidLine)
        self.addLine(SideView, 2, 1, SolidLine)
        self.addLine(SideView, 2, 0, SolidLine)

        # VerticalView
        self.addPoint(VerticalView, x=0, y=0)
        self.addPoint(VerticalView, x=1, y=0)
        self.addPoint(VerticalView, x=0, y=1)
        self.addPoint(VerticalView, x=1, y=1)
        self.addLine(VerticalView, 0, 1, SolidLine)
        self.addLine(VerticalView, 1, 3, SolidLine)
        self.addLine(VerticalView, 2, 3, SolidLine)
        self.addLine(VerticalView, 2, 0, SolidLine)
        self.addLine(VerticalView, 1, 2, SolidLine)

    def initCube(self):
        # FrontView
        self.addPoint(FrontView, y=0, z=0)
        self.addPoint(FrontView, y=1, z=0)
        self.addPoint(FrontView, y=0, z=1)
        self.addPoint(FrontView, y=1, z=1)
        self.addLine(FrontView, 0, 1, SolidLine)
        self.addLine(FrontView, 1, 3, SolidLine)
        self.addLine(FrontView, 2, 3, SolidLine)
        self.addLine(FrontView, 2, 0, SolidLine)

        # SideView
        self.addPoint(SideView, x=0, z=0)
        self.addPoint(SideView, x=1, z=0)
        self.addPoint(SideView, x=0, z=1)
        self.addPoint(SideView, x=1, z=1)
        self.addLine(SideView, 0, 1, SolidLine)
        self.addLine(SideView, 1, 3, SolidLine)
        self.addLine(SideView, 2, 3, SolidLine)
        self.addLine(SideView, 2, 0, SolidLine)

        # VerticalView
        self.addPoint(VerticalView, x=0, y=0)
        self.addPoint(VerticalView, x=1, y=0)
        self.addPoint(VerticalView, x=0, y=1)
        self.addPoint(VerticalView, x=1, y=1)
        self.addLine(VerticalView, 0, 1, SolidLine)
        self.addLine(VerticalView, 1, 3, SolidLine)
        self.addLine(VerticalView, 2, 3, SolidLine)
        self.addLine(VerticalView, 2, 0, SolidLine)


class MyMplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget（当然也是FigureCanvasAgg）"""

    def __init__(self, viewData=None, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.viewData = viewData

        FigureCanvas.__init__(self, self.fig)
        self.axes = self.fig.add_subplot(111, projection='3d')
        # 每次plot()调用的时候，我们希望原来的坐标轴被清除(所以False)
        self.axes.hold(False)
        # self.axes.figure.canvas = FigureCanvas
        # Axes3D.mouse_init(self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.computeInitialFigure()


    def computeInitialFigure(self):
        pass


class ViewNameLabel(QWidget):
    def __init__(self, text="defaultName", x=100, y=100):
        super().__init__()
        self.text = text
        self.x = x
        self.y = y
        self.initUI()

    def initUI(self):
        # self.setGeometry(300, 300, self.x, self.y)
        self.setMinimumSize(300, 20)
        self.setContentsMargins(5, 5, 5, 5)
        self.setWindowTitle("Label")
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QColor(30, 200, 30))
        qp.setFont(QFont("Decorative", 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)


class PointButton(QPushButton):
    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.setMouseTracking(False)

    def mouseMoveEvent(self, event):
        message = 'move event at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        messenger.changeStatusBar(message)

    def mouseReleaseEvent(self, event):
        message = 'release event at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())

        if event.pos().x() < 10 and event.pos().x() > 0 and event.pos().y() < 10 and event.pos().y() > 0:
            return
        x = self.pos().x() + event.pos().x()
        y = self.pos().y() + event.pos().y()
        v, index = self.text()
        # print(self.accessibleName())
        # v, index = self.accessibleName()
        index = int(index)
        if v == 'A':
            messenger.changeViewDataByPoint(FrontView, index, 0.0, (x - 100) / 100.0, (200 - y) / 100.0)
        elif v == 'B':
            messenger.changeViewDataByPoint(SideView, index, (x - 100) / 100.0, 0.0, (200 - y) / 100.0)
        elif v == 'C':
            messenger.changeViewDataByPoint(VerticalView, index, (y - 100) / 100.0, (x - 100) / 100.0, 0.0)
        else:
            pass
            # try:
            #     # 不直接修改，通过修改元数据影响
            #     # self.move(x + event.pos().x(), y + event.pos().y())
            #     # self.setGeometry(x + event.pos().x(), y + event.pos().y(), 10, 10)
            # except Exception as e:
            #     print(e)

        # 修改完成再提示
        messenger.changeStatusBar(message)

    def dragMoveEvent(self, event):
        print('dragging: ', event.pos().x(), event.pos().y())
        self.move(event.pos().x(), event.pos().y())

    def dragLeaveEvent(self, event):
        message = 'drag leave at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        messenger.changeStatusBar(message)

    def mousePressEvent(self, event):
        message = 'press at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        # print('press at point[ ', self.text(), ' ]: ', event.pos().x(), event.pos().y())
        messenger.changeStatusBar(message)


class ViewMainPainter(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        # timer = QtCore.QTimer(self)
        # timer.timeout.connect(self.update_figure)
        # timer.start(1000)

    def mousePressEvent(self, event):
        message = 'press at Main View, Area: ' + str(self.areaSum)
        messenger.changeStatusBar(message)
        super().mousePressEvent(event)

    def computeInitialFigure(self):
        # 确定立体图中的点
        # 从正视图->侧视图: z->z
        # 从侧视图->俯视图: x->x
        # 从俯视图->正视图: y->y
        self.axes.clear()
        certainPoints = []  # 确定的几何体上的点
        certainLines = []  # 确定的几何体上的边（三角面片的边）
        certainPlane = []
        planeNumForLine = {}  # 每条边上所关联的面数目
        for v in [FrontView, SideView, VerticalView]:
            self.viewType = v
            index = 0
            length = len(self.viewData.Point[self.viewType]['x'])
            for i in range(length):
                coorX = None
                coorY = None
                corrZ = None
                x, y, z = np.multiply(self.viewData.getPoint(self.viewType, i), 1)
                print('now is ' + str([x, y, z]))
                nextViewType = (self.viewType + 1) % 3
                if self.viewType is FrontView:
                    zLength = self.viewData.Point[nextViewType]['z'].count(z)
                    if zLength is 0:
                        continue
                    else:
                        coorY = y
                        zArr = []
                        lastIndex = -1
                        # 获取侧视图中，与正视图该点z坐标相同的点所在数组下标
                        for j in range(zLength):
                            lastIndex = self.viewData.Point[nextViewType]['z'].index(z, lastIndex + 1)
                            zArr.append(lastIndex)
                            print('for' + str(z) + 'add' + str(lastIndex))
                        print(zArr)
                        for k in zArr:
                            x1, y1, z1 = np.multiply(self.viewData.getPoint(nextViewType, k), 1)
                            finalViewType = (nextViewType + 1) % 3

                            xLength = self.viewData.Point[finalViewType]['x'].count(x1)
                            if xLength is 0:
                                continue
                            else:
                                coorZ = z1
                                xArr = []
                                lastIndex = -1
                                # 获取俯视图中，与侧视图y坐标相同的点所在数组下标
                                for j in range(xLength):
                                    lastIndex = self.viewData.Point[finalViewType]['x'].index(x1, lastIndex + 1)
                                    xArr.append(lastIndex)
                                    print('    for' + str(y1) + 'add' + str(lastIndex))
                                print('    ' + str(xArr))
                                for l in xArr:
                                    x2, y2, z2 = np.multiply(self.viewData.getPoint(finalViewType, l), 1)
                                    coorX = x2
                                    # 通过判断x2是否等于x，确定是否存在三垂线先交于一点
                                    if y2 == y and certainPoints.count([coorX, coorY, coorZ]) is 0:
                                        certainPoints.append([coorX, coorY, coorZ])
                                        print('    add' + str([coorX, coorY, coorZ]))
                                        # break
                                    else:
                                        print('    y2 == y is ' + str(y2 == y) + str([coorX, coorY, coorZ]))
                elif self.viewType is SideView:
                    pass
                elif self.viewType is VerticalView:
                    pass
                self.axes.hold(True)
                index += 1

        print(certainPoints)

        index = 65
        base = 0
        span = 0.8

        # 做垂线辅助线求交点，可去除
        # for v in [FrontView, SideView, VerticalView]:
        #     self.viewType = v
        #     length = len(self.viewData.Point[self.viewType]['x'])
        #     for i in range(length):
        #         x, y, z = np.multiply(self.viewData.getPoint(self.viewType, i), 1)
        #
        #         if self.viewType is FrontView:
        #             self.axes.plot((base, span), (y, y), (z, z), color='gray')
        #         elif self.viewType is SideView:
        #             self.axes.plot((x, x), (base, span), (z, z), color='gray')
        #         elif self.viewType is VerticalView:
        #             self.axes.plot((x, x), (y, y), (base, span), color='gray')
        #         else:
        #             break
        #         self.axes.hold(True)
        #         index += 1

        length = len(certainPoints)
        self.lengthForLine = []
        for i in range(length):
            self.axes.text(certainPoints[i][0], certainPoints[i][1], certainPoints[i][2], chr(65 + i), color="red")
            for j in range(i + 1, length):
                # 两两之间连线
                # self.axes.plot((certainPoints[i][0], certainPoints[j][0]),
                #                (certainPoints[i][1], certainPoints[j][1]),
                #                (certainPoints[i][2], certainPoints[j][2]), color='red')

                # 分别在三个视图中确定该直线存在是否合理
                pIndex1 = -1
                pIndex2 = -1
                isExist = 0
                x, y, z = certainPoints[i]
                x1, y1, z1 = certainPoints[j]
                for v in [FrontView, SideView, VerticalView]:
                    if v is FrontView:
                        pIndex1 = self.viewData.getPointIndex(view=FrontView, x=0.0, y=y, z=z)
                        pIndex2 = self.viewData.getPointIndex(view=FrontView, x=0.0, y=y1, z=z1)
                    elif v is SideView:
                        pIndex1 = self.viewData.getPointIndex(view=SideView, x=x, y=0.0, z=z)
                        pIndex2 = self.viewData.getPointIndex(view=SideView, x=x1, y=0.0, z=z1)
                    elif v is VerticalView:
                        pIndex1 = self.viewData.getPointIndex(view=VerticalView, x=x, y=y, z=0.0)
                        pIndex2 = self.viewData.getPointIndex(view=VerticalView, x=x1, y=y1, z=0.0)
                    else:
                        pIndex1 = -1
                        pIndex2 = -1
                    # if pIndex1 == -1:
                    #     print('pIndex1 = -1')
                    #     print(x, y, z)
                    #     print(certainPoints[i])
                    # if pIndex2 == -1:
                    #     print('pIndex2 = -1')
                    #     print(x1, y1, z1)
                    #     print(certainPoints[j])
                    if self.viewData.lineExist(v, pIndex1, pIndex2):
                        isExist += 1
                        # print(v, pIndex1, pIndex2)
                    else:
                        print('line not exist: ', v, pIndex1, pIndex2)
                        print(certainPoints[i], certainPoints[j])
                        print(self.viewData.Point[v])
                        print(self.viewData.Line[v])
                        break

                # print('isExist', isExist)
                if isExist == 3:
                    self.axes.plot((certainPoints[i][0], certainPoints[j][0]),
                                   (certainPoints[i][1], certainPoints[j][1]),
                                   (certainPoints[i][2], certainPoints[j][2]), color='green')
                    self.lengthForLine.append(np.math.sqrt(np.square(certainPoints[i][0]-certainPoints[j][0])
                                                           + np.square(certainPoints[i][1]-certainPoints[j][1])
                                                           + np.square(certainPoints[i][2]-certainPoints[j][2])))
                    certainLines.append({i, j})
                    planeNumForLine[str({i, j})] = 0
                    # 辅助线去除
                    # elif isExist == 2:
                    #     self.axes.plot((certainPoints[i][0], certainPoints[j][0]),
                    #                    (certainPoints[i][1], certainPoints[j][1]),
                    #                    (certainPoints[i][2], certainPoints[j][2]), color='blue')
                    # elif isExist == 1:
                    #     self.axes.plot((certainPoints[i][0], certainPoints[j][0]),
                    #                    (certainPoints[i][1], certainPoints[j][1]),
                    #                    (certainPoints[i][2], certainPoints[j][2]), color='yellow')

        print('certainPoints:    len: ', len(certainPoints), certainPoints)
        print('certainLines:     len: ', len(certainLines), certainLines)
        length = len(certainLines)
        # 确定几何体中的面，不适用以前的三角面判定法，改为判断几条边是否可以围成一个平面
        # 遍历所有可链接边的组合，计算是否属于同一平面，是则暂时添加入certainPlane中
        for i in range(length):
            for testPoints in (itertools.combinations(certainLines, i)):
                print(testPoints)

        # 手动计算可以组成平面的边
        for i in range(length):
            # print(certainLines)
            a, b = certainLines[i]
            tempPlane = [a, b]
            asa = {}
            leftLines = certainLines[i:]
            for leftNum in range(length):
                leftNum = length - leftNum - 1
                tempIndex = 0
                next = -1
                while leftNum > 0 and len(leftLines) > 0:
                    if a in leftLines[tempIndex]:
                        tempLine = leftLines[tempIndex].copy()
                        tempLine.remove(a)
                        next = tempLine.pop()
                        tempPlane.append(next)
                        leftLines.remove({a, next})
                        a = next
                    tempIndex += 1

                    # 首尾可相连，开始验证是否在同一平面上
                    if next == b:
                        p1, p2, p3 = tempPlane[0:3]
                        a1, b1, c1 = certainPoints[p1]
                        a2, b2, c2 = certainPoints[p2]
                        a3, b3, c3 = certainPoints[p3]
                        vectorA = np.array([a2-a1, b2-b1, c2-c1], float)
                        vectorB = np.array([a3-a1, b3-b1, c3-c1], float)
                        normal = np.cross(vectorA, vectorB)
                        dotValue = np.dot(np.array([a1, b1, c1], float), normal)
                        # 判断其他点是否在三点围成的平面上
                        testFlag = True
                        for testI in range(3, len(tempPlane)):
                            a3, b3, c3 = certainPoints[testI]
                            if dotValue != np.dot(np.array([a3, b3, c3], float), normal):
                                testFlag = False
                                break
                        if testFlag and certainPlane.count(set(tempPlane)) == 0:
                            certainPlane.append(set(tempPlane))
            # for j in range(i + 1, length):
            #     assert (len(certainLines[i]) == 2)
            #     a, b = certainLines[i]
            #     # restLines = certainLines[j].copy()
            #     # restLines.remove()
            #     if a in certainLines[j]:
            #         tempLine = certainLines[j].copy()
            #         tempLine.remove(a)
            #         c = tempLine.pop()
            #     elif b in certainLines[j]:
            #         tempLine = certainLines[j].copy()
            #         tempLine.remove(b)
            #         c = tempLine.pop()
            #     else:
            #         continue
            #     if certainLines.count({b, c}) > 0 and certainLines.count({a, c}) > 0 and certainPlane.count(
            #             {a, b, c}) == 0:
            #         certainPlane.append({a, b, c})
            #         planeNumForLine[str({a, b})] += 1
            #         planeNumForLine[str({b, c})] += 1
            #         planeNumForLine[str({a, c})] += 1

        # 去除在几何体内的面
        length = len(certainPlane)
        index = 0
        while index < length:
            try:
                a, b, c = certainPlane[index]
            except:
                print('here', index)
            if planeNumForLine[str({a, b})] > 2 and planeNumForLine[str({b, c})] > 2 and planeNumForLine[
                str({a, c})] > 2:
                planeNumForLine[str({a, b})] -= 1
                planeNumForLine[str({b, c})] -= 1
                planeNumForLine[str({a, c})] -= 1
                certainPlane.remove({a, b, c})
                index -= 1
                length -= 1
            index += 1

        print('certainPlane:     len: ', len(certainPlane), certainPlane)
        print('planeNumForLine:  len: ', len(planeNumForLine), planeNumForLine)

        areaSum = 0
        self.areaForPlane = []
        for i in range(len(certainPlane)):
            a, b, c = certainPlane[i]
            p1 = certainPoints[a]
            p2 = certainPoints[b]
            p3 = certainPoints[c]
            print(p1, p2, p3)
            area = self.viewData.countTriangleArea(p1, p2, p3)
            self.areaForPlane.append(area)
            areaSum += area
            print(area)

        self.certainPoints = certainPoints
        self.certainLines = certainLines
        self.certainPlane = certainPlane
        self.areaSum = areaSum
        print(self.areaSum)

        # length = len(self.viewData.Line[self.viewType]['s'])
        # for i in range(length):
        #     sIndex = self.viewData.Line[self.viewType]['s'][i]
        #     eIndex = self.viewData.Line[self.viewType]['e'][i]
        #     real = self.viewData.Line[self.viewType]['real'][i]
        #
        #     x, y, z = np.multiply(self.viewData.getPoint(self.viewType, sIndex), 100)
        #     x1, y1, z1 = np.multiply(self.viewData.getPoint(self.viewType, eIndex), 100)
        #
        #     if real is DashLine:
        #         pen.setStyle(QtCore.Qt.DashLine)
        #     else:
        #         pen.setStyle(QtCore.Qt.SolidLine)
        #
        #     if self.viewType is FrontView:
        #         qp.drawLine(y, z, y1, z1)
        #     elif self.viewType is SideView:
        #         qp.drawLine(x, z, x1, z1)
        #     elif self.viewType is VerticalView:
        #         qp.drawLine(x, y, x1, y1)
        #     else:
        #         break

        self.axes.set_zlabel('z')
        self.axes.set_ylabel('y')
        self.axes.set_xlabel('x')
        self.draw()

    def verifyData(self):
        certainPoints = []  # 确定的几何体上的点
        certainLines = []  # 确定的几何体上的边（三角面片的边）
        certainPlane = []
        planeNumForLine = {}  # 每条边上所关联的面数目
        for v in [FrontView, SideView, VerticalView]:
            self.viewType = v
            index = 0
            length = len(self.viewData.Point[self.viewType]['x'])
            for i in range(length):
                coorX = None
                coorY = None
                corrZ = None
                x, y, z = np.multiply(self.viewData.getPoint(self.viewType, i), 1)
                nextViewType = (self.viewType + 1) % 3
                if self.viewType is FrontView:
                    zLength = self.viewData.Point[nextViewType]['z'].count(z)
                    if zLength is 0:
                        continue
                    else:
                        coorY = y
                        zArr = []
                        lastIndex = -1
                        # 获取侧视图中，与正视图该点z坐标相同的点所在数组下标
                        for j in range(zLength):
                            lastIndex = self.viewData.Point[nextViewType]['z'].index(z, lastIndex + 1)
                            zArr.append(lastIndex)
                        for k in zArr:
                            x1, y1, z1 = np.multiply(self.viewData.getPoint(nextViewType, k), 1)
                            finalViewType = (nextViewType + 1) % 3

                            xLength = self.viewData.Point[finalViewType]['x'].count(x1)
                            if xLength is 0:
                                continue
                            else:
                                coorZ = z1
                                xArr = []
                                lastIndex = -1
                                # 获取俯视图中，与侧视图y坐标相同的点所在数组下标
                                for j in range(xLength):
                                    lastIndex = self.viewData.Point[finalViewType]['x'].index(x1, lastIndex + 1)
                                    xArr.append(lastIndex)
                                for l in xArr:
                                    x2, y2, z2 = np.multiply(self.viewData.getPoint(finalViewType, l), 1)
                                    coorX = x2
                                    # 通过判断x2是否等于x，确定是否存在三垂线先交于一点
                                    if y2 == y and certainPoints.count([coorX, coorY, coorZ]) is 0:
                                        certainPoints.append([coorX, coorY, coorZ])
                elif self.viewType is SideView:
                    pass
                elif self.viewType is VerticalView:
                    pass
                index += 1

        for v in [FrontView, SideView, VerticalView]:
            flag = False
            errorMessage = '提供三视图点数为0。'
            for i in range(len(self.viewData.Point[v]['x'])):
                print('current point: ', self.viewData.getPoint(v, i))
                x, y, z = self.viewData.getPoint(v, i)
                flag = False
                for j in certainPoints:
                    if v is FrontView and y == j[1] and z == j[2] or v is SideView and x == j[0] and z == j[2] or v is VerticalView and x == j[0] and y == j[1]:
                        flag = True
                        break
                if not flag:
                    errorMessage = '点：' + chr(65+v) + str(i) + '在生成几何体中不存在。'
                    break
            if not flag:
                reply = QMessageBox.information(aw, '错误', '数据检验失败，提供三视图无法生成几何体!\n' + errorMessage)
                return

        index = 65
        base = 0
        span = 0.8

        length = len(certainPoints)
        for i in range(length):
            for j in range(i + 1, length):
                pIndex1 = -1
                pIndex2 = -1
                isExist = 0
                x, y, z = certainPoints[i]
                x1, y1, z1 = certainPoints[j]
                for v in [FrontView, SideView, VerticalView]:
                    if v is FrontView:
                        pIndex1 = self.viewData.getPointIndex(view=FrontView, x=0.0, y=y, z=z)
                        pIndex2 = self.viewData.getPointIndex(view=FrontView, x=0.0, y=y1, z=z1)
                    elif v is SideView:
                        pIndex1 = self.viewData.getPointIndex(view=SideView, x=x, y=0.0, z=z)
                        pIndex2 = self.viewData.getPointIndex(view=SideView, x=x1, y=0.0, z=z1)
                    elif v is VerticalView:
                        pIndex1 = self.viewData.getPointIndex(view=VerticalView, x=x, y=y, z=0.0)
                        pIndex2 = self.viewData.getPointIndex(view=VerticalView, x=x1, y=y1, z=0.0)
                    else:
                        pIndex1 = -1
                        pIndex2 = -1
                    if self.viewData.lineExist(v, pIndex1, pIndex2):
                        isExist += 1
                        # print(v, pIndex1, pIndex2)
                    else:
                        break

                if isExist == 3:
                    certainLines.append({i, j})
                    planeNumForLine[str({i, j})] = 0

        length = len(certainLines)
        for i in range(length):
            for j in range(i + 1, length):
                assert (len(certainLines[i]) == 2)
                a, b = certainLines[i]
                if a in certainLines[j]:
                    tempLine = certainLines[j].copy()
                    tempLine.remove(a)
                    c = tempLine.pop()
                elif b in certainLines[j]:
                    tempLine = certainLines[j].copy()
                    tempLine.remove(b)
                    c = tempLine.pop()
                else:
                    continue
                if certainLines.count({b, c}) > 0 and certainLines.count({a, c}) > 0 and certainPlane.count(
                        {a, b, c}) == 0:
                    certainPlane.append({a, b, c})
                    planeNumForLine[str({a, b})] += 1
                    planeNumForLine[str({b, c})] += 1
                    planeNumForLine[str({a, c})] += 1

        # 去除在几何体内的面
        length = len(certainPlane)
        index = 0
        while index < length:
            try:
                a, b, c = certainPlane[index]
            except:
                print('here', index)
            if planeNumForLine[str({a, b})] > 2 and planeNumForLine[str({b, c})] > 2 and planeNumForLine[
                str({a, c})] > 2:
                planeNumForLine[str({a, b})] -= 1
                planeNumForLine[str({b, c})] -= 1
                planeNumForLine[str({a, c})] -= 1
                certainPlane.remove({a, b, c})
                index -= 1
                length -= 1
            index += 1

        for i in planeNumForLine:
            if planeNumForLine[i] != 2:
                a, b = eval(i)
                print(a, b)
                errorMessage = '边：' + chr(65+a) + chr(65+b) + '在几何体中所属面片数为' + str(planeNumForLine[i]) + '，不为2。'
                reply = QMessageBox.information(aw, '错误', '数据检验失败，提供三视图无法生成几何体!\n' + errorMessage)
                return

        reply = QMessageBox.information(aw, '提示', '数据检验成功，提供三视图可以生成几何体!')

    def drawText(self, event, qp):
        qp.setPen(QColor(30, 200, 30))
        qp.setFont(QFont("Decorative", 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)


class ViewPainter(QWidget):
    def __init__(self, viewData, viewType=FrontView):
        super().__init__()
        # 初始化三视图数据
        self.viewData = viewData
        self.viewType = viewType
        self.initUI()

    def initUI(self):

        # self.setGeometry(400, 300, 280, 170)
        # self.setMinimumSize(300, 300)
        self.setWindowTitle('绘制点')
        self.resize(500, 500)
        self.show()
        self.buttons = []
        for i in range(len(self.viewData.Point[self.viewType]['x'])):
            b = PointButton(chr(65 + self.viewType) + str(i))
            b.setToolTip('')
            b.resize(10, 10)
            b.move(100, 100)
            b.setParent(self)
            b.show()
            self.buttons.append(b)

    def mousePressEvent(self, event):
        message = 'press at view[ ' + str(self.viewType) + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        print('press at view[', self.viewType, ']: ', event.pos().x(), event.pos().y())
        messenger.changeStatusBar(message)

    def paintEvent(self, e):
        # print('painting for:', self.viewType)
        self.viewData = viewData
        # print(viewData.Point)
        # print(self.viewData.Point)
        qp = QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()

    def drawPoints(self, qp):
        qp.setPen(QtCore.Qt.red)
        size = self.size()
        length = len(self.viewData.Point[self.viewType]['x'])
        pos = []

        index = 0
        shift = 10
        for i in range(length):
            x, y, z = np.multiply(self.viewData.getPoint(self.viewType, i), 100)

            if self.viewType is FrontView:
                z = 200 - z
                y = 100 + y
                qp.drawPoint(y, z)
                qp.drawText(y + shift, z + shift, chr(65 + self.viewType) + str(index))
                pos.append([y, z])
            elif self.viewType is SideView:
                z = 200 - z
                x = 100 + x
                qp.drawPoint(x, z)
                qp.drawText(x + shift, z + shift, chr(65 + self.viewType) + str(index))
                pos.append([x, z])
            elif self.viewType is VerticalView:
                t = y
                y = 100 + x
                x = 100 + t
                qp.drawPoint(x, y)
                qp.drawText(x + shift, y + shift, chr(65 + self.viewType) + str(index))
                pos.append([x, y])
            else:
                break

            index += 1

        try:
            for i in range(length):
                self.buttons[i].move(pos[i][0], pos[i][1])
                x, y, z = self.viewData.getPoint(self.viewType, i)
                if self.viewType == FrontView:
                    x = z
                elif self.viewType == SideView:
                    y = z
                elif self.viewType == VerticalView:
                    pass
                else:
                    pass
                self.buttons[i].setToolTip('(' + str(x) + ', ' + str(y) + ')')
        except Exception as e:
            # print(e)
            pass

        length = len(self.viewData.Line[self.viewType]['s'])
        pen = QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        for i in range(length):
            sIndex = self.viewData.Line[self.viewType]['s'][i]
            eIndex = self.viewData.Line[self.viewType]['e'][i]
            real = self.viewData.Line[self.viewType]['real'][i]

            x, y, z = np.multiply(self.viewData.getPoint(self.viewType, sIndex), 100)
            x1, y1, z1 = np.multiply(self.viewData.getPoint(self.viewType, eIndex), 100)

            if real is DashLine:
                pen.setStyle(QtCore.Qt.DashLine)
            else:
                pen.setStyle(QtCore.Qt.SolidLine)

            if self.viewType is FrontView:
                z = 200 - z
                z1 = 200 - z1
                y = 100 + y
                y1 = 100 + y1
                qp.drawLine(y, z, y1, z1)
            elif self.viewType is SideView:
                z = 200 - z
                z1 = 200 - z1
                x = 100 + x
                x1 = 100 + x1
                qp.drawLine(x, z, x1, z1)
            elif self.viewType is VerticalView:
                y = 100 + y
                y1 = 100 + y1
                x = 100 + x
                x1 = 100 + x1
                # qp.drawLine(x, y, x1, y1)
                qp.drawLine(y, x, y1, x1)
            else:
                break

                # for i in range(1000):
                #     x = random.randint(1, size.width()-1)
                #     y = random.randint(1, size.height()-1)
                #     qp.drawPoint(x, y)


class PaintLine(QWidget):
    # 拖动画直线
    def __init__(self):
        super(PaintLine, self).__init__()

        self.resize(400, 300)
        self.move(100, 100)
        self.setWindowTitle('1')
        self.setMinimumSize(400, 300)

        self.setMouseTracking(False)

        self.pos_x = 20
        self.pos_y = 20

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        pen = QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        painter.drawLine(20, 20, self.pos_x, self.pos_y)
        painter.end()

    def mouseMoveEvent(self, event):
        self.pos_x = event.pos().x()
        self.pos_y = event.pos().y()
        self.update()


class PaintLines(QWidget):
    # 拖动画直线
    def __init__(self):
        super(PaintLines, self).__init__()

        self.resize(400, 300)
        self.move(100, 100)
        self.setWindowTitle('2')
        self.setMinimumSize(400, 300)

        self.setMouseTracking(False)

        self.pos_xy = []

        self.pos_x = 20
        self.pos_y = 20

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        pen = QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        for pos_tmp in self.pos_xy:
            painter.drawLine(20, 20, pos_tmp[0], pos_tmp[1])
        painter.end()

    def mouseMoveEvent(self, event):
        pos_tmp = (event.pos().x(), event.pos().y())
        self.pos_xy.append(pos_tmp)
        self.update()


class PaintTracks(QWidget):
    def __init__(self):
        super(PaintTracks, self).__init__()

        # resize设置宽高，move设置位置
        self.resize(400, 300)
        self.move(100, 100)
        self.setWindowTitle("3")
        self.setMinimumSize(400, 300)

        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)

        self.pos_xy = []

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        pen = QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        '''
            首先判断pos_xy列表中是不是至少有两个点了
            然后将pos_xy中第一个点赋值给point_start
            利用中间变量pos_tmp遍历整个pos_xy列表
                point_end = pos_tmp
                画point_start到point_end之间的线
                point_start = point_end
            这样，不断地将相邻两个点之间画线，就能留下鼠标移动轨迹了
        '''
        if len(self.pos_xy) > 1:
            point_start = self.pos_xy[0]
            for pos_tmp in self.pos_xy:
                point_end = pos_tmp
                painter.drawLine(point_start[0], point_start[1], point_end[0], point_end[1])
                point_start = point_end

        painter.end()

    def mouseMoveEvent(self, event):
        '''
            按住鼠标移动事件：将当前点添加到pos_xy列表中
            调用update()函数在这里相当于调用paintEvent()函数
            每次update()时，之前调用的paintEvent()留下的痕迹都会清空
        '''
        # 中间变量pos_tmp提取当前点
        pos_tmp = (event.pos().x(), event.pos().y())
        # pos_tmp添加到self.pos_xy中
        self.pos_xy.append(pos_tmp)

        self.update()


class PaintTrack(QWidget):
    def __init__(self):
        super(PaintTrack, self).__init__()

        # resize设置宽高，move设置位置
        self.resize(400, 300)
        self.move(100, 100)
        self.setWindowTitle("4")
        self.setMinimumSize(400, 300)

        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)

        self.pos_xy = []

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        pen = QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        '''
            首先判断pos_xy列表中是不是至少有两个点了
            然后将pos_xy中第一个点赋值给point_start
            利用中间变量pos_tmp遍历整个pos_xy列表
                point_end = pos_tmp

                判断point_end是否是断点，如果是
                    point_start赋值为断点
                    continue
                判断point_start是否是断点，如果是
                    point_start赋值为point_end
                    continue

                画point_start到point_end之间的线
                point_start = point_end
            这样，不断地将相邻两个点之间画线，就能留下鼠标移动轨迹了
        '''
        if len(self.pos_xy) > 1:
            point_start = self.pos_xy[0]
            for pos_tmp in self.pos_xy:
                point_end = pos_tmp

                if point_end == (-1, -1):
                    point_start = (-1, -1)
                    continue
                if point_start == (-1, -1):
                    point_start = point_end
                    continue

                painter.drawLine(point_start[0], point_start[1], point_end[0], point_end[1])
                point_start = point_end
        painter.end()

    def mouseMoveEvent(self, event):
        '''
            按住鼠标移动事件：将当前点添加到pos_xy列表中
            调用update()函数在这里相当于调用paintEvent()函数
            每次update()时，之前调用的paintEvent()留下的痕迹都会清空
        '''
        # 中间变量pos_tmp提取当前点
        pos_tmp = (event.pos().x(), event.pos().y())
        # pos_tmp添加到self.pos_xy中
        self.pos_xy.append(pos_tmp)

        self.update()

    def mouseReleaseEvent(self, event):
        '''
            重写鼠标按住后松开的事件
            在每次松开后向pos_xy列表中添加一个断点(-1, -1)
            然后在绘画时判断一下是不是断点就行了
            是断点的话就跳过去，不与之前的连续
        '''
        pos_test = (-1, -1)
        self.pos_xy.append(pos_test)

        self.update()


class MyStaticMplCanvas(MyMplCanvas):
    pass
    """静态画布：一条正弦线"""
    # def compute_initial_figure(self):
    #     t = arange(0.0, 3.0, 0.01)
    #     s = sin(2*pi*t)
    #     self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
    """动态画布：每秒自动更新，更换一条折线。"""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def computeInitialFigure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # 构建4个随机整数，位于闭区间[0, 10]
        l = [random.randint(0, 10) for i in range(4)]

        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()


class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("程序主窗口")

        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Open', self.loadData,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Save', self.saveData,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addAction('&Clear', self.clearData,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_D)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addAction('&Open', self.loadData)
        self.menuBar().addSeparator()
        self.menuBar().addAction('&Save', self.saveData)
        self.menuBar().addSeparator()
        self.menuBar().addAction('&Clear', self.clearData)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QWidget(self)

        # 初始化三视图数据
        global viewData
        viewData = ViewData()
        self.viewData = viewData

        globalLayout = QHBoxLayout(self.main_widget)
        l = QGridLayout(self.main_widget)
        # sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        # pl = PaintLine()
        # pls = PaintLines()
        global vpMainView
        global vpFrontView
        global vpSideView
        global vpVerticalView
        vpFrontView = ViewPainter(self.viewData, viewType=FrontView)
        vpSideView = ViewPainter(self.viewData, viewType=SideView)
        vpVerticalView = ViewPainter(self.viewData, viewType=VerticalView)
        vpMainView = ViewMainPainter(self.viewData)
        vpViews = [vpFrontView, vpSideView, vpVerticalView, vpMainView]
        self.vpMainView = vpMainView
        self.vpViews = [vpFrontView, vpSideView, vpVerticalView]
        self.graphicViews = []
        for i in range(len(vpViews)):
            self.graphicViews.append(QGraphicsView(self.main_widget))
            graphScene = QGraphicsScene()
            graphScene.addWidget(vpViews[i])
            self.graphicViews[i].setScene(graphScene)
            self.graphicViews[i].setAlignment(Qt.AlignCenter)
            self.graphicViews[i].verticalScrollBar().hide()
            self.graphicViews[i].horizontalScrollBar().hide()
            self.graphicViews[i].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.graphicViews[i].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.graphicViews[i].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.graphicViews[i].setMinimumSize(500, 300)

        dataLayout = QGridLayout(self.main_widget)
        line = 0
        self.viewComboBox = QComboBox()
        self.viewComboBox.insertItem(0, self.tr("正视图"))
        self.viewComboBox.insertItem(1, self.tr("侧视图"))
        self.viewComboBox.insertItem(2, self.tr("俯视图"))
        self.viewComboBox.insertItem(3, self.tr("主视图"))
        self.viewComboBox.setCurrentIndex(3)
        self.viewComboBox.currentIndexChanged.connect(messenger.viewChanged)
        self.buttons = []
        for i in range(10):
            temp = QPushButton()
            temp.setFixedSize(40, 20)
            temp.setAccessibleName(str(i))
            temp.clicked.connect(lambda: messenger.buttonClicked(self.sender().accessibleName()))
            self.buttons.append(temp)
        self.buttons[0].setText('新增')
        self.buttons[1].setText('修改')
        self.buttons[2].setText('删除')
        self.buttons[3].setText('新增')
        self.buttons[4].setText('删除')
        self.buttons[5].setText('查询')
        self.buttons[6].setText('检验')
        self.buttons[7].setText('生成')
        self.buttons[8].setText('报告')
        self.buttons[9].setText('查询')
        spaceLabels = []
        for i in range(4):
            spaceLabel = QLabel('------------------------------------')
            spaceLabel.setFixedHeight(20)
            spaceLabels.append(spaceLabel)
        propLabels = []
        for n in ['点','线','面','几何体']:
            propLabel = QLabel(n)
            propLabel.setFixedHeight(20)
            propLabels.append(propLabel)
        self.dataLineEdits = []
        for n in range(9):
            temp = QLineEdit()
            self.dataLineEdits.append(temp)

        dataLayout.setSpacing(5)
        dataLayout.addWidget(QLabel('当前视图：'), line, 0)
        dataLayout.addWidget(self.viewComboBox, line, 1, 1, 3)
        line += 1
        dataLayout.addWidget(spaceLabels[0], line, 0, 1, 6)
        line += 1
        dataLayout.addWidget(propLabels[0], line, 0)
        line += 1
        dataLayout.addWidget(QLabel('名称'), line, 0)
        dataLayout.addWidget(self.dataLineEdits[0], line, 1)
        line += 1
        dataLayout.addWidget(QLabel('坐标'), line, 0)
        dataLayout.addWidget(self.dataLineEdits[1], line, 1)
        dataLayout.addWidget(QLabel(','), line, 2)
        dataLayout.addWidget(self.dataLineEdits[2], line, 3)
        dataLayout.addWidget(QLabel(','), line, 4)
        dataLayout.addWidget(self.dataLineEdits[3], line, 5)
        line += 1
        dataLayout.addWidget(self.buttons[0], line, 1)
        dataLayout.addWidget(self.buttons[1], line, 3)
        dataLayout.addWidget(self.buttons[2], line, 5)
        line += 1
        dataLayout.addWidget(spaceLabels[1], line, 0, 1, 6)
        line += 1
        dataLayout.addWidget(propLabels[1], line, 0)
        line += 1
        dataLayout.addWidget(QLabel('端点'), line, 0)
        dataLayout.addWidget(self.dataLineEdits[4], line, 1)
        dataLayout.addWidget(QLabel('-'), line, 2)
        dataLayout.addWidget(self.dataLineEdits[5], line, 3)
        line += 1
        dataLayout.addWidget(QLabel('长度'), line, 0)
        self.lengthLabel = QLabel('10')
        self.lengthLabel.setFixedHeight(30)
        dataLayout.addWidget(self.lengthLabel, line, 1, 1, 6)
        line += 1
        dataLayout.addWidget(self.buttons[3], line, 1)
        dataLayout.addWidget(self.buttons[4], line, 3)
        dataLayout.addWidget(self.buttons[9], line, 5)
        line += 1
        dataLayout.addWidget(spaceLabels[2], line, 0, 1, 6)
        line += 1
        dataLayout.addWidget(propLabels[2], line, 0)
        line += 1
        dataLayout.addWidget(QLabel('端点'), line, 0)
        dataLayout.addWidget(self.dataLineEdits[6], line, 1)
        dataLayout.addWidget(QLabel('-'), line, 2)
        dataLayout.addWidget(self.dataLineEdits[7], line, 3)
        dataLayout.addWidget(QLabel('-'), line, 4)
        dataLayout.addWidget(self.dataLineEdits[8], line, 5)
        line += 1
        dataLayout.addWidget(QLabel('面积'), line, 0)
        self.areaLabel = QLabel('10')
        self.areaLabel.setFixedHeight(30)
        # self.areaLabel.setFixedSize(30, 20)
        dataLayout.addWidget(self.areaLabel, line, 1, 1, 6)
        line += 1
        dataLayout.addWidget(self.buttons[5], line, 1)
        line += 1
        dataLayout.addWidget(spaceLabels[3], line, 0, 1, 6)
        line += 1
        dataLayout.addWidget(propLabels[3], line, 0)
        line += 1
        dataLayout.addWidget(QLabel('点数'), line, 0)
        self.pointNumLabel = QLabel('6')
        self.pointNumLabel.setFixedSize(30, 20)
        dataLayout.addWidget(self.pointNumLabel)
        line += 1
        dataLayout.addWidget(QLabel('线段数'), line, 0)
        self.lineNumLabel = QLabel('12')
        self.lineNumLabel.setFixedSize(30, 20)
        dataLayout.addWidget(self.lineNumLabel)
        line += 1
        dataLayout.addWidget(QLabel('三角面数'), line, 0)
        self.areaNumLabel = QLabel('8')
        self.areaNumLabel.setFixedSize(30, 20)
        dataLayout.addWidget(self.areaNumLabel)
        line += 1
        dataLayout.addWidget(self.buttons[6], line, 1)
        dataLayout.addWidget(self.buttons[7], line, 3)
        dataLayout.addWidget(self.buttons[8], line, 5)

        # 填充
        line += 1
        dataLayout.addWidget(QLabel(''), line, 0, 5, 1)

        # pt = PaintTrack()
        # pts = PaintTracks()
        # pts1 = PaintTracks()
        # dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        labels = [ViewNameLabel(text="正视图"), ViewNameLabel(text="侧视图"),
                  ViewNameLabel(text="俯视图"), ViewNameLabel(text="主视图")]
        l.addWidget(self.graphicViews[0], 0, 0)
        l.addWidget(self.graphicViews[1], 0, 1)
        l.addWidget(self.graphicViews[2], 2, 0)
        l.addWidget(self.graphicViews[3], 2, 1)
        # l.addWidget(vpFrontView, 0, 0)
        # l.addWidget(vpSideView, 0, 1)
        # l.addWidget(vpVerticalView, 2, 0)
        # l.addWidget(vpMainView, 2, 1)
        l.addWidget(labels[0], 1, 0)
        l.addWidget(labels[1], 1, 1)
        l.addWidget(labels[2], 3, 0)
        l.addWidget(labels[3], 3, 1)
        self.gridLayout = l
        globalLayout.addLayout(self.gridLayout)
        globalLayout.addLayout(dataLayout)
        messenger.setup(self.statusBar(), self.viewData)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        # 状态条显示2秒
        self.statusBar().showMessage("Deal Line: 2017.12.23")
        # self.statusBar().showMessage("转换中", 10000)
        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        # self.setGeometry(0, 0, self.gridLayout.totalSizeHint().width(), self.gridLayout.totalSizeHint().height())
        self.setGeometry(0, 0, 1000, 800)
        size = self.geometry()
        self.setGeometry((screen.width() - size.width()) / 2,
                         (screen.height() - size.height()) / 2, 900, 900)
        print((screen.width() - size.width()) / 2,
              (screen.height() - size.height()) / 2, 900, 900)

    def center1(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def loadData(self):
        self.clearData()
        f, t = QFileDialog.getOpenFileName()
        print(f)
        try:
            inputFile = open(f, 'rb')
            aw.viewData.Point = pickle.load(inputFile)
            aw.viewData.Line = pickle.load(inputFile)
            for viewType in [FrontView, SideView, VerticalView]:
                aw.vpViews[viewType].buttons = []
                for i in range(len(self.viewData.Point[viewType]['x'])):
                    b = PointButton(chr(65 + viewType) + str(i))
                    b.setToolTip('')
                    b.resize(10, 10)
                    b.move(100, 100)
                    b.setParent(aw.vpViews[viewType])
                    b.show()
                    aw.vpViews[viewType].buttons.append(b)
                aw.vpViews[viewType].repaint()
        except Exception as e:
            reply = QMessageBox.information(aw, '错误', '载入数据文件失败!')
            print(e)

    def saveData(self):
        f, t = QFileDialog.getSaveFileName()
        print(f)
        try:
            output = open(f, 'wb')
            pickle.dump(aw.viewData.Point, output)
            pickle.dump(aw.viewData.Line, output)
            output.flush()
            output.close()
        except Exception as e:
            reply = QMessageBox.information(aw, '错误', '保存数据文件失败!')
            print(e)

    def clearData(self):
        for viewType in [FrontView, SideView, VerticalView]:
            aw.viewData.Point[viewType]['x'].clear()
            aw.viewData.Point[viewType]['y'].clear()
            aw.viewData.Point[viewType]['z'].clear()
            aw.viewData.Line[viewType]['s'].clear()
            aw.viewData.Line[viewType]['e'].clear()
            aw.viewData.Line[viewType]['real'].clear()
            aw.vpViews[viewType].repaint()
            try:
                for i in aw.vpViews[viewType].buttons:
                    i.deleteLater()
                    # aw.vpViews[viewType].buttons.remove(i)
                aw.vpViews[viewType].buttons = []
            except Exception as e:
                print(e)
        aw.vpMainView.computeInitialFigure()

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QMessageBox.about(self, "About",
                          """
    1.	平面图转3D主要功能如下：
    a)	提供三视图生成对应立体图
    b)	拖动三视图点实时改变立体图
    c)	拖动立体图点实时改变三视图
    d)	计算立体表面积
        """
                          )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # a = ViewNameLabel(text="here")
    aw = ApplicationWindow()
    aw.setWindowTitle("三视图转化")
    aw.show()
    # sys.exit(qApp.exec_())
    app.exec_()
