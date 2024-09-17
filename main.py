#!/usr/bin/env python
__author__ = "whw"

import pygame
import time
import random
import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk

root = tk.Tk()


class MainWindow():
    __gameTitle = "月饼消消乐"
    __windowWidth = 700  # 窗口宽度
    __windowHeigth = 500  # 窗口高度
    __icons = []
    __gameSize = 10  # 游戏尺寸
    __iconKind = __gameSize * __gameSize / 4  # 小图片种类数量
    __iconWidth = 40  # 小图片宽度
    __iconHeight = 40  # 小图片高度
    __map = []  # 游戏地图
    __delta = 25
    __isFirst = True
    __isGameStart = False
    __formerPoint = None

    EMPTY = -1
    NONE_LINK = 0
    STRAIGHT_LINK = 1
    ONE_CORNER_LINK = 2
    TWO_CORNER_LINK = 3

    # 新增倒计时相关变量，初始化为 500 秒
    __countdown_time = 500
    __timer_id = None

    def __init__(self):
        root.title(self.__gameTitle)
        self.centerWindow(self.__windowWidth, self.__windowHeigth)
        root.minsize(460, 460)
        self.__addComponets()
        self.extractSmallIconList()
        # 初始化倒计时定时器
        self.__update_countdown()

    # 音乐播放
    def play(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load('music/music1.mp3')
            pygame.mixer.music.play(5)
            time.sleep(1)
        except pygame.error as e:
            print(f"音乐播放错误：{e}")

    # 停止播放音乐
    def stop(self):
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"音乐停止错误：{e}")

    def __addComponets(self):
        # 定义菜单栏
        self.menubar = tk.Menu(root, bg="lightgrey", fg="black")
        self.file_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.file_menu.add_command(label="新游戏", command=self.file_new)
        self.menubar.add_cascade(label="开始游戏", menu=self.file_menu)
        self.menubar.add_command(label="播放音乐", command=self.play_music)
        self.menubar.add_command(label="关闭音乐", command=self.stop_music)
        # 添加退出游戏按钮
        self.menubar.add_command(label="退出游戏", command=self.exit_game)
        root.configure(menu=self.menubar)
        # 地图尺寸、颜色
        self.canvas = tk.Canvas(root, bg='lightblue', width=450, height=450)
        # 插入图片
        try:
            self.image_file = tk.PhotoImage(file='images/img_3.png')
            self.image = self.canvas.create_image(100, 80, anchor='nw', image=self.image_file)
        except tk.TclError as e:
            print(f"图片加载错误：{e}")
        # 插入文字
        try:
            self.text = self.canvas.create_text(100, 100, anchor='nw', text='月饼消消乐', fill="green",
                                                font=('宋体', 30))
        except tk.TclError as e:
            print(f"文字创建错误：{e}")
        self.canvas.pack(side=tk.TOP, pady=5)
        self.canvas.bind('<Button-1>', self.clickCanvas)
        # 在界面上显示倒计时
        self.countdown_label = tk.Label(root, text=f"倒计时：{self.__countdown_time} 秒", font=("Arial", 12))
        self.countdown_label.pack(side=tk.TOP)

    # 中心窗口尺寸
    def centerWindow(self, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)

    def file_new(self):
        self.iniMap()
        self.drawMap()
        self.__isGameStart = True
        # 重置倒计时
        self.__countdown_time = 500
        self.__update_countdown()

    def play_music(self):
        self.play()

    def stop_music(self):
        self.stop()

    def clickCanvas(self, event):
        if self.__isGameStart:
            point = self.getInnerPoint(Point(event.x, event.y))
            # 有效点击坐标
            if point.isUserful() and not self.isEmptyInMap(point):
                if self.__isFirst:
                    self.drawSelectedArea(point)
                    self.__isFirst = False
                    self.__formerPoint = point
                else:
                    if self.__formerPoint.isEqual(point):
                        self.__isFirst = True
                        self.canvas.delete("rectRedOne")
                    else:
                        link_type = self.getLinkType(self.__formerPoint, point)
                        if link_type['type']!= self.NONE_LINK:
                            self.ClearLinkedBlocks(self.__formerPoint, point)
                            self.canvas.delete("rectRedOne")
                            self.__isFirst = True
                            # 游戏结束，弹出提示
                            if self.isGameEnd():
                                tk.messagebox.showinfo("温馨提示：", "You Win！")
                                self.__isGameStart = False
                                # 停止倒计时定时器
                                if self.__timer_id is not None:
                                    root.after_cancel(self.__timer_id)
                        else:
                            self.__formerPoint = point
                            self.canvas.delete("rectRedOne")
                            self.drawSelectedArea(point)

    # 判断游戏是否结束
    def isGameEnd(self):
        for y in range(0, self.__gameSize):
            for x in range(0, self.__gameSize):
                if self.__map[y][x]!= self.EMPTY:
                    return False
        return True

    # 获取小图片数组
    def extractSmallIconList(self):
        try:
            imageSouce = Image.open('images/little.png')
            for index in range(0, int(self.__iconKind)):
                region = imageSouce.crop((self.__iconWidth * index, 0,
                                          self.__iconWidth * index + self.__iconWidth - 1, self.__iconHeight - 1))
                self.__icons.append(ImageTk.PhotoImage(region))
        except FileNotFoundError as e:
            print(f"图片文件未找到：{e}")

    # 初始化地图，存值为 0-24
    def iniMap(self):
        self.__map = []  # 重置地图
        tmpRecords = []
        records = []
        for i in range(0, int(self.__iconKind)):
            for j in range(0, 4):
                tmpRecords.append(i)

        total = self.__gameSize * self.__gameSize
        for x in range(0, total):
            index = random.choice(tmpRecords)
            records.append(index)
            tmpRecords.remove(index)

        # 一维数组转为二维，y 为高维度
        for y in range(0, self.__gameSize):
            for x in range(0, self.__gameSize):
                if x == 0:
                    self.__map.append([])
                self.__map[y].append(records[x + y * self.__gameSize])

    # 根据地图绘制图像
    def drawMap(self):
        try:
            self.canvas.delete("all")
            for y in range(0, self.__gameSize):
                for x in range(0, self.__gameSize):
                    point = self.getOuterLeftTopPoint(Point(x, y))
                    im = self.canvas.create_image((point.x, point.y),
                                                  image=self.__icons[self.__map[y][x]], anchor='nw', tags='im%d%d' % (x, y))
        except tk.TclError as e:
            print(f"图像绘制错误：{e}")

    # 获取内部坐标对应矩形左上角顶点坐标
    def getOuterLeftTopPoint(self, point):
        return Point(self.getX(point.x), self.getY(point.y))

    # 获取内部坐标对应矩形中心坐标
    def getOuterCenterPoint(self, point):
        return Point(self.getX(point.x) + int(self.__iconWidth / 2),
                     self.getY(point.y) + int(self.__iconHeight / 2))

    def getX(self, x):
        return x * self.__iconWidth + self.__delta

    def getY(self, y):
        return y * self.__iconHeight + self.__delta

    # 获取内部坐标
    def getInnerPoint(self, point):
        x = -1
        y = -1

        for i in range(0, self.__gameSize):
            x1 = self.getX(i)
            x2 = self.getX(i + 1)
            if point.x >= x1 and point.x < x2:
                x = i

        for j in range(0, self.__gameSize):
            j1 = self.getY(j)
            j2 = self.getY(j + 1)
            if point.y >= j1 and point.y < j2:
                y = j

        return Point(x, y)

    # 选择的区域变红，point 为内部坐标
    def drawSelectedArea(self, point):
        pointLT = self.getOuterLeftTopPoint(point)
        pointRB = self.getOuterLeftTopPoint(Point(point.x + 1, point.y + 1))
        try:
            self.canvas.create_rectangle(pointLT.x, pointLT.y,
                                         pointRB.x - 1, pointRB.y - 1, outline='red', tags="rectRedOne")
        except tk.TclError as e:
            print(f"绘制选中区域错误：{e}")

    # 消除连通的两个块
    def ClearLinkedBlocks(self, p1, p2):
        self.__map[p1.y][p1.x] = self.EMPTY
        self.__map[p2.y][p2.x] = self.EMPTY
        try:
            self.canvas.delete('im%d%d' % (p1.x, p1.y))
            self.canvas.delete('im%d%d' % (p2.x, p2.y))
        except tk.TclError as e:
            print(f"删除图像错误：{e}")

    # 地图上该点是否为空
    def isEmptyInMap(self, point):
        if self.__map[point.y][point.x] == self.EMPTY:
            return True
        else:
            return False

    # 获取两个点连通类型
    def getLinkType(self, p1, p2):
        # 首先判断两个方块中图片是否相同
        if self.__map[p1.y][p1.x]!= self.__map[p2.y][p2.x]:
            return {'type': self.NONE_LINK}
        # 判断是否为直接连通
        if self.isStraightLink(p1, p2):
            return {
                'type': self.STRAIGHT_LINK
            }
        # 判断是否为单拐点连通
        res = self.isOneCornerLink(p1, p2)
        if res:
            return {
                'type': self.ONE_CORNER_LINK,
                'p1': res
            }
        # 判断是否为双拐点连通
        res = self.isTwoCornerLink(p1, p2)
        if res:
            return {
                'type': self.TWO_CORNER_LINK,
                'p1': res['p1'],
                'p2': res['p2']
            }
        return {
            'type': self.NONE_LINK
        }

    # 直连：选中的两个方块在同一行或同一列
    def isStraightLink(self, p1, p2):
        start = -1
        end = -1
        # 水平
        if p1.y == p2.y:
            # 大小判断
            if p2.x < p1.x:
                start = p2.x
                end = p1.x
            else:
                start = p1.x
                end = p2.x
            for x in range(start + 1, end):
                if self.__map[p1.y][x]!= self.EMPTY:
                    return False
            return True
        elif p1.x == p2.x:
            if p1.y > p2.y:
                start = p2.y
                end = p1.y
            else:
                start = p1.y
                end = p2.y
            for y in range(start + 1, end):
                if self.__map[y][p1.x]!= self.EMPTY:
                    return False
            return True
        return False

    # 单拐点连通
    def isOneCornerLink(self, p1, p2):
        pointCorner = Point(p1.x, p2.y)
        if self.isStraightLink(p1, pointCorner) and self.isStraightLink(pointCorner, p2) and self.isEmptyInMap(
                pointCorner):
            return pointCorner

        pointCorner = Point(p2.x, p1.y)
        if self.isStraightLink(p1, pointCorner) and self.isStraightLink(pointCorner, p2) and self.isEmptyInMap(
                pointCorner):
            return pointCorner

    # 双拐点连通
    def isTwoCornerLink(self, p1, p2):
        for y in range(-1, self.__gameSize + 1):
            pointCorner1 = Point(p1.x, y)
            pointCorner2 = Point(p2.x, y)
            if y == p1.y or y == p2.y:
                continue
            if y == -1 or y == self.__gameSize:
                if self.isStraightLink(p1, pointCorner1) and self.isStraightLink(pointCorner2, p2):
                    return {'p1': pointCorner1, 'p2': pointCorner2}
            else:
                if self.isStraightLink(p1, pointCorner1) and self.isStraightLink(pointCorner1,
                                                                                 pointCorner2) and self.isStraightLink(
                    pointCorner2, p2) and self.isEmptyInMap(pointCorner1) and self.isEmptyInMap(pointCorner2):
                    return {'p1': pointCorner1, 'p2': pointCorner2}
        # 横向判断
        for x in range(-1, self.__gameSize + 1):
            pointCorner1 = Point(x, p1.y)
            pointCorner2 = Point(x, p2.y)
            if x == p1.x or x == p2.x:
                continue
            if x == -1 or x == self.__gameSize:
                if self.isStraightLink(p1, pointCorner1) and self.isStraightLink(pointCorner2, p2):
                    return {'p1': pointCorner1, 'p2': pointCorner2}
            else:
                if self.isStraightLink(p1, pointCorner1) and self.isStraightLink(pointCorner1,
                                                                                 pointCorner2) and self.isStraightLink(
                    pointCorner2, p2) and self.isEmptyInMap(pointCorner1) and self.isEmptyInMap(pointCorner2):
                    return {'p1': pointCorner1, 'p2': pointCorner2}

    # 更新倒计时
    def __update_countdown(self):
        if self.__countdown_time > 0:
            self.__countdown_time -= 1
            self.countdown_label.config(text=f"倒计时：{self.__countdown_time} 秒")
            self.__timer_id = root.after(1000, self.__update_countdown)
        else:
            # 倒计时结束，显示游戏失败
            tk.messagebox.showinfo("温馨提示：", "时间到！游戏结束")
            self.__isGameStart = False
            # 停止倒计时定时器
            if self.__timer_id is not None:
                root.after_cancel(self.__timer_id)

    def exit_game(self):
        try:
            root.destroy()
        except tk.TclError as e:
            print(f"退出游戏错误：{e}")


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def isUserful(self):
        if self.x >= 0 and self.y >= 0:
            return True
        else:
            return False

    # 判断两个点是否相同
    def isEqual(self, point):
        if self.x == point.x and self.y == point.y:
            return True
        else:
            return False

    # 克隆一份对象
    def clone(self):
        return Point(self.x, self.y)

    # 改为另一个对象
    def changeTo(self, point):
        self.x = point.x
        self.y = point.y

m = MainWindow()
root.mainloop()