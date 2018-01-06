import sys
import random

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt


from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QGridLayout, QSizePolicy, QMessageBox, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget（当然也是FigureCanvasAgg）"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # 每次plot()调用的时候，我们希望原来的坐标轴被清除(所以False)
        self.axes.hold(False)
        # self.axes = plt.axes([0.025, 0.025, 0.95, 0.95])  # [xmin,ymin,xmax,ymax]

        self.axes.set_xlim(0, 4)
        self.axes.set_ylim(0, 3)
        self.axes.xaxis.set_major_locator(plt.MultipleLocator(1.0))  # 设置x主坐标间隔 1
        self.axes.xaxis.set_minor_locator(plt.MultipleLocator(0.1))  # 设置x从坐标间隔 0.1
        self.axes.yaxis.set_major_locator(plt.MultipleLocator(1.0))  # 设置y主坐标间隔 1
        self.axes.yaxis.set_minor_locator(plt.MultipleLocator(0.1))  # 设置y从坐标间隔 0.1
        self.axes.grid(which='major', axis='x', linewidth=0.75, linestyle='-', color='0.75')  # 由每个x主坐标出发对x主坐标画垂直于x轴的线段
        self.axes.grid(which='minor', axis='x', linewidth=0.25, linestyle='-', color='0.75')  # 由每个x主坐标出发对x主坐标画垂直于x轴的线段
        self.axes.grid(which='major', axis='y', linewidth=0.75, linestyle='-', color='0.75')
        self.axes.grid(which='minor', axis='y', linewidth=0.25, linestyle='-', color='0.75')
        self.axes.set_xticklabels([])  # 标记x轴主坐标的值,在这里设为空值，则表示坐标无数值标定；其他情况如

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class ViewNameLabel(QWidget):
    def __init__(self, text="defaultName", x=100, y=100):
        super().__init__()
        self.text = text
        self.x = x
        self.y = y
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, self.x, self.y)
        self.setMinimumSize(400, 30)
        self.setWindowTitle("Label")
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont("Decorative", 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)


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

        #resize设置宽高，move设置位置
        self.resize(400, 300)
        self.move(100, 100)
        self.setWindowTitle("4")
        self.setMinimumSize(400, 300)

        #setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
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
        #中间变量pos_tmp提取当前点
        pos_tmp = (event.pos().x(), event.pos().y())
        #pos_tmp添加到self.pos_xy中
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
    def compute_initial_figure(self):
        ax = plt.axes([0.025, 0.025, 0.95, 0.95])  # [xmin,ymin,xmax,ymax]

        ax.set_xlim(0, 4)
        ax.set_ylim(0, 3)
        ax.xaxis.set_major_locator(plt.MultipleLocator(1.0))  # 设置x主坐标间隔 1
        ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))  # 设置x从坐标间隔 0.1
        ax.yaxis.set_major_locator(plt.MultipleLocator(1.0))  # 设置y主坐标间隔 1
        ax.yaxis.set_minor_locator(plt.MultipleLocator(0.1))  # 设置y从坐标间隔 0.1
        ax.grid(which='major', axis='x', linewidth=0.75, linestyle='-', color='0.75')  # 由每个x主坐标出发对x主坐标画垂直于x轴的线段
        ax.grid(which='minor', axis='x', linewidth=0.25, linestyle='-', color='0.75')  # 由每个x主坐标出发对x主坐标画垂直于x轴的线段
        ax.grid(which='major', axis='y', linewidth=0.75, linestyle='-', color='0.75')
        ax.grid(which='minor', axis='y', linewidth=0.25, linestyle='-', color='0.75')
        ax.set_xticklabels([])  # 标记x轴主坐标的值,在这里设为空值，则表示坐标无数值标定；其他情况如
        # ax.set_xticklabels([i for i in range(10)])
        self.axes = ax
        self.axes.plot = plt

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

    def compute_initial_figure(self):
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
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QWidget(self)

        l = QGridLayout(self.main_widget)
        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        pl = PaintLine()
        pls = PaintLines()
        pt = PaintTrack()
        pts = PaintTracks()
        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        labels = [ViewNameLabel(text="正视图"), ViewNameLabel(text="侧视图"),
                  ViewNameLabel(text="俯视图"), ViewNameLabel(text="主视图")]
        l.addWidget(sc, 0, 0)
        l.addWidget(pl, 1, 0)
        l.addWidget(pls, 0, 1)
        l.addWidget(dc, 1, 2)
        l.addWidget(pts, 0, 2)
        l.addWidget(pt, 1, 1)
        l.addWidget(labels[0], 2, 0)
        l.addWidget(labels[1], 2, 1)
        l.addWidget(labels[2], 2, 2)


        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        # 状态条显示2秒
        self.statusBar().showMessage("转换中", 10000)

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
    #sys.exit(qApp.exec_())
    app.exec_()
