# coding:utf-8
#import res
import math
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Slot, QUrl, QSize, QFile, QTextStream, QThread, Signal, QRect
from PySide2.QtGui import QIcon, QPainterPath, QPainter, QBrush, QColor, QPen
import sys
from PySide2.QtWidgets import QTableWidget, QProgressBar, QTextBrowser, QHeaderView, QTableWidgetItem, \
    QGraphicsDropShadowEffect

import re
import log
import time
import jieba
from urllib import parse
from urllib import request
from bs4 import BeautifulSoup
import threading
from wordcloud import WordCloud
from collections import Counter
import numpy as np
# import matplotlib.pylab as plt
import matplotlib
from matplotlib import pyplot as plt
class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(1000, 700)  # 1000,700
        self.main_widget = QtWidgets.QWidget()  # 创建窗口主部件

        self.left_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.left_widget.setObjectName('left_widget')
        self.left_widget.setFixedSize(300,700)
        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.right_widget.setFixedSize(700, 676)
        self.right_up_widget = QtWidgets.QWidget()
        self.right_up_widget.setFixedSize(700,20)
        # 左侧菜单栏
        # 爬取部分
        self.left_crawl_label = QtWidgets.QPushButton("信息爬取")
        self.left_crawl_label.setObjectName('left_label')
        self.left_keyword_label = QtWidgets.QLabel(chr(0xf002) + ' ' + '关键词')
        self.left_keyword_search_input = QtWidgets.QLineEdit()
        self.left_pagenum_label = QtWidgets.QLabel(chr(0xf002) + ' ' + '搜索页数')
        self.left_pagenum_search_input = QtWidgets.QLineEdit()
        self.left_crawl_button = QtWidgets.QPushButton("开始爬取")
        self.left_crawl_button.setObjectName('left_button_spider')
        self.left_stopcrawl_button = QtWidgets.QPushButton("停止爬取")
        self.left_stopcrawl_button.setObjectName('left_button_spider')
        # 分析部分
        self.left_analysize_label = QtWidgets.QPushButton("数据分析")
        self.left_analysize_label.setObjectName('left_label')
        self.left_title_analyse_button = QtWidgets.QPushButton("题目关联")
        self.left_title_analyse_button.setObjectName('left_button')
        self.left_author_button = QtWidgets.QPushButton("相关学者")
        self.left_author_button.setObjectName('left_button')
        self.left_researchYear_button = QtWidgets.QPushButton("研究趋势")
        self.left_researchYear_button.setObjectName('left_button')
        self.left_publisher_button = QtWidgets.QPushButton("相关机构")
        self.left_publisher_button.setObjectName('left_button')
        self.left_quoteNum_button = QtWidgets.QPushButton("引用数")
        self.left_quoteNum_button.setObjectName('left_button')
        self.left_abstract_button = QtWidgets.QPushButton("摘要关键")
        self.left_abstract_button.setObjectName('left_button')
        # 右侧显示栏
        self.right_close = QtWidgets.QPushButton("")  # 关闭按钮
        self.right_mini = QtWidgets.QPushButton("")  # 最小化按钮
        self.right_table = QTableWidget(self)  # 表格栏
        self.right_progressbar = QProgressBar(self)  # 进度条
        self.right_browser = QTextBrowser(self)#信息栏

        self.crawl_thread = CrawlThread()#实例化一个对象

        self.layout_init()
        self.btn_function_init()
        self.table_init()
        self.setStytle()
        self.crawl_init()

    def layout_init(self):
        #总布局
        self.main_layout = QtWidgets.QGridLayout()  # 创建主窗口布局
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setLayout(self.main_layout)  # 设置主窗口布局
        self.left_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_widget.setLayout(self.left_layout)  # 设置左侧部件布局为网格

        self.right_layout = QtWidgets.QGridLayout()
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格
        # self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.right_up_layout = QtWidgets.QGridLayout()
        self.right_up_widget.setLayout(self.right_up_layout)
        self.right_up_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.left_widget, 0, 0, 12, 4)  # 左侧部件在第0行第0列，占8行3列  1000
        self.main_layout.addWidget(self.right_up_widget,0,5,1,10) #左上栏
        self.main_layout.addWidget(self.right_widget, 1,5, 11, 10)  # 右侧部件在第0行第3列，占8行9列

        # 左侧布局分布
        # 爬取部分
        self.left_layout.addWidget(self.left_crawl_label, 1, 0, 1, 3)
        self.left_layout.addWidget(self.left_keyword_label, 2, 0, 1, 2)
        self.left_layout.addWidget(self.left_keyword_search_input, 2, 2, 1, 1)
        self.left_layout.addWidget(self.left_pagenum_label, 3, 0, 1, 2)
        self.left_layout.addWidget(self.left_pagenum_search_input, 3, 2, 1, 1)
        self.left_layout.addWidget(self.left_crawl_button, 4, 0, 1, 4)
        self.left_layout.addWidget(self.left_stopcrawl_button,5,0,1,4)
        # 分析部分
        self.left_layout.addWidget(self.left_analysize_label, 6, 0, 1, 3)
        self.left_layout.addWidget(self.left_title_analyse_button, 7, 0, 1, 3)
        self.left_layout.addWidget(self.left_author_button, 8, 0, 1, 3)
        self.left_layout.addWidget(self.left_researchYear_button, 9, 0, 1, 3)
        self.left_layout.addWidget(self.left_publisher_button, 10, 0, 1, 3)
        self.left_layout.addWidget(self.left_quoteNum_button, 11, 0, 1, 3)
        self.left_layout.addWidget(self.left_abstract_button, 12, 0, 1, 3)

        self.right_up_layout.addWidget(self.right_mini, 0,2,1,1)
        self.right_up_layout.addWidget(self.right_close, 0,3,1,1)

        self.right_layout.addWidget(self.right_table)
        self.right_layout.addWidget(self.right_progressbar)
        self.right_layout.addWidget(self.right_browser)

        self.setCentralWidget(self.main_widget)  # 设置窗口主部件

    def btn_function_init(self):
        #left
        self.left_crawl_button.setCursor(QtCore.Qt.PointingHandCursor)#鼠标箭头变为手势
        self.left_stopcrawl_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.left_title_analyse_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.left_author_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.left_researchYear_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.left_publisher_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.left_quoteNum_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.left_abstract_button.setCursor(QtCore.Qt.PointingHandCursor)

        self.left_crawl_button.clicked.connect(lambda: self.btn_slot(self.left_crawl_button))
        self.left_stopcrawl_button.clicked.connect(lambda: self.btn_slot(self.left_stopcrawl_button))


        #数据分析
        self.left_title_analyse_button.clicked.connect(lambda: self.CountName(6,'题目关联领域频率最高'))
        self.left_author_button.clicked.connect(lambda: self.CountName(1,'发表文章的作者'))
        self.left_publisher_button.clicked.connect(lambda: self.CountName(2,'出版设出版'))
        self.left_quoteNum_button.clicked.connect(lambda: self.QuoteNum())
        self.left_abstract_button.clicked.connect(lambda:self.makeWordCloud(self.splitword()))
        self.left_researchYear_button.clicked.connect(lambda:self.PublishTime())

        #right
        self.right_close.clicked.connect(lambda: self.on_pushButton_clicked_close())#关闭窗口
        self.right_close.setCursor(QtCore.Qt.PointingHandCursor)
        self.right_mini.clicked.connect(lambda: self.on_pushButton_2_clicked_min())#最小化窗口
        self.right_mini.setCursor(QtCore.Qt.PointingHandCursor)

        self.right_progressbar.setRange(0, 100)  # 进度条范围设置为100
        self.right_progressbar.setValue(0)
    def btn_slot(self, btn):  # 将按钮的槽函数和clicked信号连接起，2、用开始、停止按钮控制线程，将线程开始停止放在槽函数中
        # self.btn_sound.play()  # 播放开始的声音
        if btn == self.left_crawl_button:
            self.right_browser.clear()  # 每次点击爬取按钮，都先调用clear()方法清空log_browser日志显示框
            self.right_browser.append('<font color="red">开始爬取</font>')
            self.right_table.clearContents()
            self.right_table.setRowCount(0)
            # self.start_btn.setEnabled(False)
            # self.stop_btn.setEnabled(True)
            # self.save_combobox.setEnabled(False)
            # 输入框
            global subject
            global pageNum
            subject = self.left_keyword_search_input.text()
            pageNum = self.left_pagenum_search_input.text()
            self.right_browser.append('搜索的关键词为：'+subject)

            self.crawl_thread.start()  # start()方法来启动线程
        else:
            self.right_browser.append('<font color="red">停止爬取</font>')
            # self.stop_btn.setEnabled(False)
            # self.start_btn.setEnabled(True)
            # self.save_combobox.setEnabled(True)

            self.crawl_thread.terminate()  # terminate()终止线程
    def crawl_init(self):
        # self.crawl_thread.finished_signal.connect(self.finish_slot)
        self.crawl_thread.log_signal.connect(self.set_log_slot)
        self.crawl_thread.result_signal.connect(self.set_table_slot)
    def table_init(self):
        self.right_table.setColumnCount(7)  # 设置表格控件的列数
        self.right_table.setHorizontalHeaderLabels(['题名', '作者', '来源', '发表时间', '被引数', '摘要','相关领域'])  # 将表格割裂标题设置成要爬取的数据字段名称
        self.right_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 将标题栏各列的宽度模式设置为拉伸
    def set_table_slot(self, title, rating, people_num, author_info, pub_info, year_info,caption_filed):
        row = self.right_table.rowCount()
        self.right_table.insertRow(row)

        self.right_table.setItem(row, 0, QTableWidgetItem(title))
        self.right_table.setItem(row, 1, QTableWidgetItem(rating))
        self.right_table.setItem(row, 2, QTableWidgetItem(people_num))
        self.right_table.setItem(row, 3, QTableWidgetItem(author_info))
        self.right_table.setItem(row, 4, QTableWidgetItem(pub_info))
        self.right_table.setItem(row, 5, QTableWidgetItem(year_info))
        self.right_table.setItem(row, 6, QTableWidgetItem(caption_filed))

        percentage = int(((row + 1) / (int(pageNum) * 10)) * 100)
        self.right_progressbar.setValue(percentage)
        #
        # if self.right_progressbar.value() == 100:
        #     self.finish_sound.play()
    def set_log_slot(self, new_log):
        self.right_browser.append(new_log)
    #****************左侧数据分析按钮功能***********************************************************************************
    def splitword(self):
        txt = ''
        for row in range(self.right_table.rowCount()):
            txt += self.right_table.item(row, 5).text().lower()  #读取文本
        for ch in [' a ', ' b ', ' c ', ' d ', ' e ', ' f ', ' g ', ' h ', ' i ', ' j ', ' k ', ' l ', ' m ', ' n ',
                   ' o ', ' p ', ' q ', ' r ', ' s ', ' t ', ' u ', ' v ', ' w ', ' x ', ' y ', ' z ',
                   'has', 'but', 'have', 'been', 'this', 'the','and','as','is','that','for','which','The','while','one','two','abstract','Abstract','with','are','can','from','what'
                   ]:
            if ch in txt:
                txt = txt.replace(ch, "")
        seg_list = jieba.cut(txt)
        c = Counter()
        result = {}
        for x in seg_list:
            if len(x) > 2 and x != '\r\n':
                c[x] += 1
        for (k, v) in c.most_common():
            result[k] = v  # 放到字典中，用于生成词云的源数据

        return result

    def makeWordCloud(self,txt):
        x, y = np.ogrid[:300, :500]

        mask = (x - 150) ** 2 + (y - 150) ** 2 > 150 ** 2
        mask = 255 * mask.astype(int)

        wc = WordCloud(background_color="white",
                       max_words=500,
                       mask=mask,
                       repeat=True,
                       width=1000,
                       height=1000,
                       scale=15,  # 这个数值越大，产生的图片分辨率越高，字迹越清晰
                       font_path="C:\Windows\Fonts\Arial.TTF")
        # print(txt)
        wc.generate_from_frequencies(txt)
        # wc.to_file(‘abc.png‘)

        plt.axis("off")
        plt.imshow(wc, interpolation="bilinear")
        plt.show()

    def CountName(self,num_col,stranalyse):#作者是1，出版社是2，关联领域是6
        text,old_text ='',''
        outnum = 0
        for row in range(self.right_table.rowCount()):
            old_text=self.right_table.item(row, num_col).text().strip()
            if len(old_text) <1:
                continue
            else:
                text += old_text
                if int(num_col) ==6:
                    text += "|"
                else:
                    text +='·'
        if int(num_col) ==6:
            words = text.split('|')
        else:
            words = text.split('·')
        # words = re.split('·|',text)

        for numi in words:
            if len(numi)<1:
                words.remove(numi)
        c = Counter(words)
        self.right_browser.append(stranalyse+'数量前十名是')
        while outnum<10:
            self.right_browser.append(str(c.most_common(10)[outnum][0]))#堆问题解决top-n
            self.right_browser.append("数量："+str(c.most_common(10)[outnum][1]))
            outnum += 1
        if int(num_col) == 6:
            self.KeyCakePic(c)
        elif int(num_col) ==1:
            self.Author_H(c)
        elif int(num_col)==2:
            self.Author_H(c)

    def KeyCakePic(self,c):
        values = []
        labels = []  # 绘图显示的标签
        outnum = 0
        while outnum<10:
            labels.append(str(c.most_common(10)[outnum][0]))#堆问题解决top-n
            values.append(int(c.most_common(10)[outnum][1]))
            outnum += 1
        colors = ['#1F92CE', '#FB9901', '#FA5307', '#D0EA2C']
        # explode = [0, 0.1, 0] # 旋转角度
        plt.figure(figsize=(20, 12), dpi=150)
        plt.title("Related Fields", fontsize=25)  # 标题
        plt.pie(values, labels=labels, colors=colors,
                startangle=180,
                radius=5,
                textprops={'fontsize':18,'color':'k'},
                shadow=True,
                autopct='%1.1f%%')
        # for t in l_text:
        #     t.set_size = (50)
        # for t in p_text:
        #     t.set_size = (50)
        plt.axis('equal')
        plt.show()

    def Author_H(self, c):
        x_pic = []
        y_pic = []  # 绘图显示的标签
        outnum = 0
        while outnum<10:
            x_pic.append(str(c.most_common(10)[outnum][0]))#堆问题解决top-n
            y_pic.append(int(c.most_common(10)[outnum][1]))
            outnum += 1
        plt.figure(figsize=(20, 10), dpi=200)
        # 柱子总数
        N = 10
        index = np.arange(N)
        # 柱子的宽度
        width = 0.45
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        colors = ['#FF0000','#FF7F00','#FFFF00','#00FF00','#00FFFF','#0000FF','#8B00FF']
        p2 = plt.bar(x_pic, y_pic, width, label="num", color=colors)
        plt.xlabel('Name')
        plt.ylabel('Number')
        plt.title('Name-Number')
        plt.legend(loc="upper right")
        plt.show()

    def PublishTime(self):
        datevalue,datahighnum =[],[]
        for row in range(self.right_table.rowCount()):
            leixing = self.right_table.item(row, 3).text()
            if len(leixing) == 0:
                continue
            else:
                leixing = int(leixing)
            if leixing not in datevalue and leixing:
                datevalue.append(leixing)
                datahighnum.append(1)
            indexnum = datevalue.index(leixing)
            datahighnum[indexnum] = datahighnum[indexnum] + 1
        together = zip(datevalue, datahighnum)
        together2 = sorted(together, key=lambda x: x[0])
        x_value, y_value = zip(*together2)

        # 根据数据绘制图形

        fig = plt.figure(dpi=128, figsize=(10, 6))
        # 实参alpha指定颜色的透明度，0表示完全透明，1（默认值）完全不透明
        plt.plot(x_value,y_value,c='red', alpha=0.5)
        # plt.plot(dates,lows,c='blue',alpha=0.5)
        # 给图表区域填充颜色
        # plt.fill_between(dates,highs,lows,facecolor='blue',alpha=0.1)
        plt.title('Publication time distribution', fontsize=24)
        plt.xlabel('Year', fontsize=16)
        plt.ylabel('Number of papers', fontsize=16)
        plt.tick_params(axis='both', which='major', labelsize=16)
        # 绘制斜的日期标签
        fig.autofmt_xdate()
        plt.show()

    def QuoteNum(self):
        title_tabletext, author_tabletext,quotenum_table = [], [],[]
        for row in range(self.right_table.rowCount()):
            title_tabletext.append(self.right_table.item(row,0).text())#题目
            author_tabletext.append(self.right_table.item(row,1).text()) #作者
            quotenum_table_old = self.right_table.item(row,4).text()
            if quotenum_table_old is '':
                quotenum_table_num = int(0)
            else:
                quotenum_table_num=int(quotenum_table_old)
            quotenum_table.append(quotenum_table_num)#被引数
        together1 = zip(title_tabletext,author_tabletext,quotenum_table)
        together2 = sorted(together1,key=lambda x:x[2],reverse=True)
        d = {}
        x_value,y_value,z_value = zip(*together2)

        for rownum in range(0,5):
            self.right_browser.append('题目为：'+str(x_value[rownum])+'\n作者：'+ str(y_value[rownum])+'\n引用数：'+str(z_value[rownum]))

    def pointpic(self):
        x_values = []
        y_values = []
        for row in range(self.table.rowCount()):
            marknum = float(self.table.item(row, 1).text())
            peonum = float(self.table.item(row,2).text())
            x_values.append(marknum)
            y_values.append(peonum)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.scatter(x_values, y_values, s=50)

        # 设置图表标题并给坐标轴加上标签
        plt.title('评分和评论数的相关性', fontsize=24)
        plt.xlabel('JudgeMark', fontsize=14)
        plt.ylabel('Peoplenumber', fontsize=14)

        # 设置刻度标记的大小
        plt.tick_params(axis='both', which='major', labelsize=14)
        plt.show()


    def setStytle(self):
        self.right_close.setFixedSize(15, 15)  # 设置关闭按钮的大小
        self.right_mini.setFixedSize(15, 15)  # 设置最小化按钮大小
        self.right_close.setIcon(QIcon('res/delete.svg'))
        self.right_mini.setIcon(QIcon('res/min.svg'))
        #关闭和最小化栏
        self.right_close.setStyleSheet('''
            QPushButton:hover{background:red;border-radius:10px}''')
        self.right_mini.setStyleSheet('''
            QPushButton:hover{background:rgb(0,255,0);border-radius:10px}''')
        self.right_up_widget.setStyleSheet('''
            QWidget{background:rgb(240,240,240);border-top-right-radius:10px;}''')
        #右侧
        self.right_widget.setStyleSheet('''
            QWidget{background:rgb(240,240,240);} 
            QTableWidget{background:rgb(255,255,255);border-radius:10px;}
            
            QProgressBar{background:rgb(255,255,255);border-radius:10px; text-align:center;color: black;}
            QProgressBar::chunk {background: rgb(230, 9, 42);border-radius:10px;}
            
            QTextBrowser{background:rgb(255,255,255);border-radius:10px;}
            
            QHeaderView{border: none;border-bottom: 3px solid #532A2A;background: #BC8F8F;min-height: 30px;color:#532A2A;font-size:16px;font-family:"Helvetica Neue", Helvetica, Arial, sans-serif}
            QHeaderView::section:horizontal{border: none;color: white;font-weight:800;background: transparent;}
            QHeaderView::section:vertical{border: none;color: white;background: transparent;}
            QHeaderView::section:horizontal:hover{background: rgb(230, 39, 39);}
            QHeaderView::section:horizontal:pressed{background: rgb(255, 0, 0);}
            QHeaderView::section:vertical:hover{background: rgb(230, 39, 39);}
            QHeaderView::section:vertical:pressed{background: rgb(255, 0, 0);
        }''')
        self.left_widget.setStyleSheet('''
            QWidget#left_widget{background:gray;
                border-top:1px solid gray;
                border-bottom:1px solid gray;
                border-left:1px solid gray;
                border-top-left-radius:10px;
                border-bottom-left-radius:10px;
             }
            QPushButton{border:none;color:white;}
            QPushButton#left_label{
                border:none;
                border-bottom:1px solid white;
                font-size:22px;
                font-weight:800;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
             }
             QPushButton#left_button:hover{border-left:5px solid red;font-weight:700;}
             QPushButton#left_button_spider{font-size:18px;font-weight:700;}
             QPushButton#left_button_spider:hover{
                border-left:5px solid red;
                font-size:20px;
                font-weight:750;
                color:black;
             }
             QLineEdit{
                border:1px solid gray;
                width:300px;
                border-radius:10px;
                padding:2px 4px;
            }
            QLabel{
                border:none;
                color:white;
                font-size:16px;
                font-weight:500;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }''')
        # self.setWindowOpacity(0.98)  # 设置窗口透明度
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框

        self.shadow = QGraphicsDropShadowEffect()#设置阴影
        self.shadow.setOffset(0,0)
        self.shadow.setColor(QColor("#444444"))
        self.shadow.setBlurRadius(30)
        self.main_widget.setGraphicsEffect(self.shadow)
        self.main_layout.setMargin(3)

        self.main_layout.setSpacing(0)

    # 拖动无边框窗口
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if QtCore.Qt.LeftButton:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    @Slot()
    def on_pushButton_clicked_close(self):  # 关闭
        self.close()

    @Slot()
    def on_pushButton_2_clicked_min(self):  # 最小化
        self.showMinimized()


logger = log.Logger().get_logger()
Headers = {
    "Upgrade-Insecure-Requests": "1",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,la;q=0.7,pl;q=0.6",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
}
Base_URL = "https://cn.bing.com/academic/search?"

class CrawlThread(QThread):  # 用pyqt5时将线程类改成QThread
    finished_signal = Signal()
    log_signal = Signal(str)
    result_signal = Signal(str, str, str, str, str, str,str)

    def __init__(self):
        super(CrawlThread, self).__init__()

    def download_html(self, url, retry, delay):
        try:
            req = request.Request(url=url, headers=Headers)
            resp = request.urlopen(req, timeout=5)
            # req = urllib.request.Request(url=url, headers=Headers)
            # html = urllib.request.urlopen(req).read().decode('utf-8')
            if resp.status != 200:
                logger.error('url open error. url = {}'.format(url))

            html_doc = resp.read()

            if html_doc == None or html_doc.strip() == '':
                logger.error('NULL html_doc')
            return html_doc
        except Exception as e:
            logger.error("failed and retry to download url {} delay = {}".format(url, delay))
            if retry > 0:
                time.sleep(delay)
                retry -= 1
                return self.download_html(url, retry, delay)

    pattern = re.compile('[0-9]+')  # 匹配字符串中是否含有数字

    def main_spider(self, keyword, pagenum):
        query = {}
        query['q'] = keyword
        pagenum = int(pagenum)
        for i in range(pagenum):
            pagenum = 1 + i * 10
            query['first'] = str(pagenum)
            url = Base_URL + parse.urlencode(query)
            html = self.download_html(url, 5, 3)
            bs = BeautifulSoup(html, "html.parser")
            list_soup = bs.find('ol', {'id': 'b_results'})
            for artical_info in list_soup.find_all('li', {'class': 'aca_algo'}):
                title,author_name, pubYear, publisher, citedNum,abstract,caption_filed = '', '', '','','','',''
                try:
                    title = artical_info.find('h2').get_text()
                except:
                    pass
                try:
                    author_name = artical_info.find('div', {'class': 'caption_author'}).get_text()
                except:
                    pass
                try:  # 输出时间，出版社，被引数
                    publish_message = artical_info.find('div', {'class': 'caption_venue'}).get_text()
                    nowmessage = re.split('[·|]', publish_message)

                    if len(nowmessage) == 3:  # 表示有出版社，出版时间，被引数
                        pubYear = nowmessage[0].strip()
                        publisher = nowmessage[1].strip()
                        citedNum = ''.strip().join(list(filter(lambda ch: ch in '0123456789.-', nowmessage[2])))
                    elif len(nowmessage) == 2:
                        match = self.pattern.findall(nowmessage[1])
                        if match:  # 如有数字，说明没有出版社信息
                            pubYear = nowmessage[0].strip()
                            publisher = 'No-Message'
                            citedNum = ''.strip().join(list(filter(lambda ch: ch in '0123456789.-', nowmessage[1])))
                        else:  # 若没有数字，说明没有引用数信息
                            pubYear = nowmessage[0].strip()
                            publisher = nowmessage[1].strip()
                            citedNum = '0'
                    else:
                        pubYear = nowmessage[0].strip()
                        publisher = 'No-Message'
                        citedNum = '0'
                except:
                    pass
                try:  # 摘要
                    abstract = artical_info.find('div', {'class': 'caption_abstract'}).get_text()
                except:
                    pass
                try:
                    caption_filed_old = artical_info.find('div', {'class': 'caption_field'})
                    fild = caption_filed_old.find_all('a')
                    for i in range(len(fild)):
                        msg = fild[i].string
                        caption_filed += msg
                        caption_filed += '|'
                except:
                    pass
                self.result_signal.emit(title,author_name,publisher,pubYear,citedNum,abstract,caption_filed)
    def run(self):
        self.main_spider(subject, pageNum)
        self.log_signal.emit('<font color="red">全部爬取完毕！</font>')

def main(app):
    gui = MainUi()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main(app)
