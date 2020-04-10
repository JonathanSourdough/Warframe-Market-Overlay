from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys
import copy
import pickle

# import pynput

from system_hotkey import SystemHotkey
import imagetrier
import multiprocessing
import multiprocessing.pool
import imagemethodcalc
import json
import time
import os
import time
import webbrowser


def scaleFactor():  # scale function, 1-2
    return settingsDict["scale"][0] / 10 + 1


class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass

    daemon = property(_get_daemon, _set_daemon)


class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


def updateInfo(windows):
    global importantInfo
    for v in windows:
        currinfoWindow = instance.infoWindowdict[v]
        curritemInfo = currinfoWindow.itemInfo
        if curritemInfo == None:
            return
        if settingsDict["listing"][0] == 0:
            listingType = "sell"
        else:
            listingType = "buy"
        try:
            ducatEfficency = str(
                round(
                    importantInfo["itemsDucat"][curritemInfo[0]]
                    / importantInfo["itemsOrderscheapest"][listingType][curritemInfo[0]][1],
                    2,
                )
            )
        except ZeroDivisionError:
            ducatEfficency = "0"
        except KeyError:
            ducatEfficency = "0"
        currinfoWindow.labelTextdict["relicItem"].setText("Item: " + curritemInfo[0])
        currinfoWindow.labelTextdict["relicAccuracy"].setText("Accuracy: " + curritemInfo[1])
        currinfoWindow.labelTextdict["platinumPlayer"].setText(
            "Top "
            + listingType
            + "er: "
            + str(importantInfo["itemsOrderscheapest"][listingType][curritemInfo[0]][0])
        )
        currinfoWindow.labelTextdict["platinumPrice"].setText(
            "Top plat: "
            + str(importantInfo["itemsOrderscheapest"][listingType][curritemInfo[0]][1])
        )
        currinfoWindow.labelTextdict["platinumAvg"].setText(
            "Top 10 Avg: "
            + str(round(importantInfo["itemsOrdersaverage"][listingType][curritemInfo[0]], 2))
        )
        try:
            currinfoWindow.labelTextdict["ducatValue"].setText(
                "Ducats: " + str(importantInfo["itemsDucat"][curritemInfo[0]])
            )
        except KeyError:
            currinfoWindow.labelTextdict["ducatValue"].setText(
                "Ducats: " + str("Not Listed on WFM")
            )
        currinfoWindow.labelTextdict["efficencyValue"].setText("Efficency: " + ducatEfficency[:4])


def updateScan(event):
    startTime = time.time()
    updateDatabase()
    global importantInfo
    pool = MyPool()
    multiprocessing.Process().daemon = False
    starMapargs = []
    for k, v in instance.searchWindowdict.items():
        starMapargs.append((k, v.geometry().getCoords(), primePartsnames))
    result = pool.starmap(imagetrier.processFoo, starMapargs)
    windows = []
    for v in result:
        windows.append(v[0])
        instance.infoWindowdict[v[0]].itemInfo = v[1]
    pool.close()
    pool.terminate()
    pool.join()
    updateInfo(windows)


def updateDatabase():
    global importantInfo, primePartsnames
    importantInfo, primePartsnames = imagemethodcalc.getImportantinfo()


def hideWindows(event):
    for tk, v in instance.windowTypes.items():
        for tk, sv in v.items():
            sv.setVisible(not sv.isVisible())


def loadMedia():  # load all the media
    if settingsDict["globalRadio"][0] == 0:  # dont load if global radio is says no
        Media["Background"] = QImage(cwd + r"\Media\Background.jpeg")  # load background
    mediaLoadLoop(iconLoadnames, "QPixmap")  # load Info Icons
    mediaLoadLoop(dropLoadnames, "QPixmap")  # load drop menu media
    mediaLoadLoop(mainLoadnames, "QPixmap")  # load main window media
    mediaLoadLoop(radioLoadnames, "QPixmap")  # load radio buttons
    mediaLoadLoop(layoutsLoadnames, "QPixmap")  # load layout media
    mediaLoadLoop(frameLoadnames, "QImage")  # load frame media
    Media["TRCorner"] = Media["TLCorner"].mirrored(
        horizontally=True, vertically=False
    )  # load the rest of the frame corners based off the top left corner
    Media["BLCorner"] = Media["TLCorner"].mirrored(horizontally=False, vertically=True)
    Media["BRCorner"] = Media["TLCorner"].mirrored(horizontally=True, vertically=True)


def mediaLoadLoop(names, imageType):  # loading all the media in the lists
    for v in names:  # for all the load names
        if imageType == "QImage":
            Media[v] = QImage(cwd + r"\Media\\" + v + ".png")  # load as Image
        if imageType == "QPixmap":
            Media[v] = QPixmap(cwd + r"\Media\\" + v + ".png")  # Load as Pixmap


class dropConstructorclass(QWidget):  # drop menu constructor
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QPushButton {background-color: transparent;}")
        self.parent = parent
        self.dropButtondict = {}
        self.dropListouterLayout = QHBoxLayout()
        self.dropListouterLayout.addStretch(0)
        self.dropListouterLayout.setContentsMargins(5 * scaleFactor(), 5 * scaleFactor(), 0, 0)
        self.dropListinnerLayout = QVBoxLayout()
        self.dropListinnerLayout.setSpacing(0)
        self.dropListsubinnerLayout = QHBoxLayout()
        self.dropListsubinnerLayout.addStretch(0)
        self.dropButton = QPushButton(self, icon=Media["DropIcon"])
        self.dropButton.setIconSize(QSize(16 * scaleFactor(), 16 * scaleFactor()))
        self.dropButton.setFixedSize(QSize(16 * scaleFactor(), 16 * scaleFactor()))
        self.dropButton.pressed.connect(lambda self=self: self.parent.dropListToggle())
        self.dropListsubinnerLayout.addWidget(self.dropButton)
        self.dropListinnerLayout.addLayout(self.dropListsubinnerLayout)
        for v in self.parent.dropIcons:
            self.dropButtondict[v] = QPushButton(self, icon=Media[v])
            self.dropButtondict[v].setIconSize(QSize(45 * scaleFactor(), 20 * scaleFactor()))
            self.dropButtondict[v].setFixedSize(QSize(45 * scaleFactor(), 20 * scaleFactor()))
            self.dropButtondict[v].clicked.connect(
                lambda checked="checked", v=v, self=self: self.parent.dropListfunc(v)
            )
            self.dropListinnerLayout.addWidget(self.dropButtondict[v])
            self.dropButtondict[v].hide()
        self.dropListinnerLayout.setContentsMargins(0, 0, 5 * scaleFactor(), 5 * scaleFactor())
        self.dropListinnerLayout.addStretch(0)
        self.dropListouterLayout.addLayout(self.dropListinnerLayout)
        self.setLayout(self.dropListouterLayout)
        self.parent.dropVis = False
        self.setSizePos()

    def setSizePos(self):
        self.move(self.parent.width() - self.width(), 0)
        self.setFixedHeight(self.parent.height())


class radioButtonclass(QRadioButton):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        if self.isChecked() is True:
            painter.drawPixmap(
                QRect(0, 0, 16 * scaleFactor(), 16 * scaleFactor()),
                Media["RadioOnIcon"],
                Media["RadioOnIcon"].rect(),
            )
        elif self.isChecked() is False:
            painter.drawPixmap(
                QRect(0, 0, 16 * scaleFactor(), 16 * scaleFactor()),
                Media["RadioOffIcon"],
                Media["RadioOnIcon"].rect(),
            )


class radioConstructorclass(QWidget):
    def __init__(self, parent, settingList, xOptions, yOptions):
        super().__init__(parent)
        self.settingList = settingList
        self.xOptions = xOptions
        self.yOptions = yOptions
        self.parent = parent
        self.radiobox = QHBoxLayout()
        self.grid = QGridLayout()
        self.radioGrouplist = []
        self.radioList = []
        self.radioLabelslist = []
        self.names = []
        for i in range(len(self.xOptions)):
            self.radioLabelslist.append(QLabel(self.xOptions[i], self))
            self.radioLabelslist[-1].setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
            self.names.append(self.radioLabelslist[-1])
        self.names.append(QLabel("", self))
        for Y in range(len(self.yOptions)):
            self.radioGrouplist.append(QButtonGroup())
            radioSet = settingList[Y]
            for X in range(len(self.xOptions)):
                radioEnum = len(self.radioList)
                self.radioList.append(radioButtonclass(self))
                self.radioGrouplist[Y].addButton(self.radioList[radioEnum], X)
                if X == radioSet:
                    self.radioList[-1].setChecked(1)
                self.names.append(self.radioList[-1])
            self.radioGrouplist[Y].buttonClicked.connect(
                lambda button, Y=Y: parent.radioCheck(button, Y, settingList)
            )
            self.radioLabelslist.append(QLabel(self.yOptions[Y], self))
            self.radioLabelslist[-1].setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
            self.names.append(self.radioLabelslist[-1])
        self.positions = [
            (Y, X) for Y in range(len(self.yOptions) + 1) for X in range(len(self.xOptions) + 1)
        ]
        for position, name in zip(self.positions, self.names):
            if name != "":
                if name.__class__.__name__ == "radioButtonclass":
                    self.grid.addWidget(name, *position, alignment=Qt.AlignCenter)
                else:
                    self.grid.addWidget(name, *position)
        self.radiobox.addLayout(self.grid)
        self.radiobox.addStretch(0)


class instanceWindow(QWidget):
    globalSettingwindowDict = {}
    searchWindowdict = {}
    infoWindowdict = {}
    settingWindowdict = {}
    windowTypes = {
        "globalSettingwindow": globalSettingwindowDict,
        "searchWindow": searchWindowdict,
        "infoWindow": infoWindowdict,
        "settingWindow": settingWindowdict,
    }

    def __init__(self, **kwargs):
        QWidget.__init__(self)
        self.windowDesignation = kwargs["windowDesignation"]
        self.pressed = False
        self.itemPressed = []
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def newSearchwindow(self):
        for i in range(100):
            if not i in self.searchWindowdict:
                self.searchWindowdict[i] = searchWindow(windowDesignation=i)
                self.searchWindowdict[i].windowDesignation = i
                # Info Windows
                self.infoWindowdict[i] = infoWindow(windowDesignation=i)
                self.infoWindowdict[i].windowDesignation = i
                return

    def newGlobalsettingWindow(self):
        if not 0 in self.globalSettingwindowDict:
            self.globalSettingwindowDict[0] = globalSettingwindow(windowDesignation=0)

    def loadWindowsettings(self):
        if self.windowDesignation not in settingsDict:
            settingsDict[self.windowDesignation] = {}
        if self.__class__.__name__ not in settingsDict[self.windowDesignation]:
            settingsDict[self.windowDesignation][self.__class__.__name__] = copy.deepcopy(
                defaultDict[self.__class__.__name__]
            )
            settingsDict[self.windowDesignation]["radio"] = copy.deepcopy(defaultDict["radio"])
        self.move(
            settingsDict[self.windowDesignation][self.__class__.__name__]["posX"],
            settingsDict[self.windowDesignation][self.__class__.__name__]["posY"],
        )
        self.resize(
            settingsDict[self.windowDesignation][self.__class__.__name__]["sizeX"],
            settingsDict[self.windowDesignation][self.__class__.__name__]["sizeY"],
        )

    def drawContainer(self, painter):
        painter.drawImage(
            QRect(0, 5 * scaleFactor(), 5 * scaleFactor(), self.height() - 10 * scaleFactor()),
            Media["VBar"],
        )
        painter.drawImage(
            QRect(
                self.width() - 5 * scaleFactor(),
                5 * scaleFactor(),
                5 * scaleFactor(),
                self.height() - 10 * scaleFactor(),
            ),
            Media["VBar"],
        )
        painter.drawImage(
            QRect(5 * scaleFactor(), 0, self.width() - 10 * scaleFactor(), 5 * scaleFactor()),
            Media["HBar"],
        )
        painter.drawImage(
            QRect(
                5 * scaleFactor(),
                self.height() - 5 * scaleFactor(),
                self.width() - 10 * scaleFactor(),
                5 * scaleFactor(),
            ),
            Media["HBar"],
        )
        painter.drawImage(QRect(0, 0, 5 * scaleFactor(), 5 * scaleFactor()), Media["TLCorner"])
        painter.drawImage(
            QRect(self.width() - 5 * scaleFactor(), 0, 5 * scaleFactor(), 5 * scaleFactor()),
            Media["TRCorner"],
        )
        painter.drawImage(
            QRect(0, self.height() - 5 * scaleFactor(), 5 * scaleFactor(), 5 * scaleFactor()),
            Media["BLCorner"],
        )
        painter.drawImage(
            QRect(
                self.width() - 5 * scaleFactor(),
                self.height() - 5 * scaleFactor(),
                5 * scaleFactor(),
                5 * scaleFactor(),
            ),
            Media["BRCorner"],
        )

    def drawLinked(self, painter):
        updateList = [self.searchWindowdict, self.infoWindowdict, self.settingWindowdict]
        if not self.windowDesignation in self.settingWindowdict:
            if (self.searchWindowdict[self.windowDesignation].DoubleClick == True) or (
                self.infoWindowdict[self.windowDesignation].DoubleClick == True
            ):
                painter.fillRect(self.rect(), QColor(100, 200, 100, 120))
                if self.linkedHighlight == False:
                    self.updateWindows(updateList[0:2], self.windowDesignation)
                    self.linkedHighlight = True
            elif (self.DoubleClick == False) and (self.linkedHighlight == True):
                self.updateWindows(updateList[0:2], self.windowDesignation)
                self.linkedHighlight = False
        else:
            if (
                (self.searchWindowdict[self.windowDesignation].DoubleClick == True)
                or (self.infoWindowdict[self.windowDesignation].DoubleClick == True)
                or (self.settingWindowdict[self.windowDesignation].DoubleClick == True)
            ):
                painter.fillRect(self.rect(), QColor(100, 200, 100, 120))
                if self.linkedHighlight == False:
                    self.updateWindows(updateList[0:3], self.windowDesignation)
                    self.linkedHighlight = True
            elif (self.DoubleClick == False) and (self.linkedHighlight == True):
                self.updateWindows(updateList[0:3], self.windowDesignation)
                self.linkedHighlight = False

    def checkFrame(self, pressPos):
        if pressPos.x() < 5 * scaleFactor():
            self.itemPressed.append("L")
        elif (self.width() - pressPos.x()) < 5 * scaleFactor():
            self.itemPressed.append("R")
        if pressPos.y() < 5 * scaleFactor():
            self.itemPressed.append("T")
        elif (self.height() - pressPos.y()) < 5 * scaleFactor():
            self.itemPressed.append("B")
        if self.itemPressed == []:
            self.itemPressed.append("Body")

    def dropListfunc(self, v):
        self.dropListToggle()
        if v == "NewIcon":
            self.newSearchwindow()
        elif v == "CloseIcon":
            self.checkLastwindow(self.__class__.__name__, self.windowDesignation)
        elif v == "SettingIcon":
            if not self.windowDesignation in self.settingWindowdict:
                self.settingWindowdict[self.windowDesignation] = settingWindow(
                    windowDesignation=self.windowDesignation
                )
        elif v == "GlobalIcon":
            self.newGlobalsettingWindow()
        elif v == "CloseAllIcon":
            self.closeAll()
        elif v == "QuitIcon":
            app.quit()
        elif v == "ResetIcon":
            global settingsDict
            for k in list(settingsDict.keys()):
                self.closeAll()
                settingsDict = layoutsDict["default"]

    def dropListToggle(self):
        self.dropVis = not self.dropVis
        for tk, v in self.dropMenu.dropButtondict.items():
            v.setVisible(self.dropVis)
        if self.dropVis:
            self.dropMenu.dropButton.setIcon(Media["DropDulledIcon"])
            self.dropMenu.raise_()
        else:
            self.dropMenu.dropButton.setIcon(Media["DropIcon"])
            self.dropMenu.lower()

    def updateFrame(self, event):
        if self.pressed == True:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.oldPos = event.globalPos()
            if (self.itemPressed != []) or ("Drop" not in self.itemPressed):
                w, h = self.width(), self.height()
                minW, minH = self.minimumWidth(), self.minimumHeight()
                x, y = self.x(), self.y()
                dx, dy = delta.x(), delta.y()
                wScale, hScale = (minW - 4 * scaleFactor(), minH - 4 * scaleFactor())
                gx, gy = event.globalPos().x(), event.globalPos().y()
                if "Body" in self.itemPressed:
                    self.move(x + dx, y + dy)
                else:
                    if self.__class__.__name__ == "searchWindow":
                        if (
                            ("L" in self.itemPressed)
                            and (w - dx >= minW)
                            and (gx - dx <= x + w - wScale)
                        ):
                            self.move(self.x() + dx, self.y())
                            self.resize(self.width() - dx, self.height())
                            # self.move(x + dx, y)
                            # self.resize(w - dx, h)
                        elif (
                            ("R" in self.itemPressed)
                            and (w + dx >= minW)
                            and (gx - dx >= x - wScale)
                        ):
                            self.resize(self.width() + dx, self.height())
                            # self.resize(w + dx, h)
                        if (
                            ("T" in self.itemPressed)
                            and (h - dy >= minH)
                            and (gy - dy <= y + h - hScale)
                        ):
                            self.move(self.x(), self.y() + dy)
                            self.resize(self.width(), self.height() - dy)
                            # self.move(x, y + dy)
                            # self.resize(w, h - dy)
                        elif (
                            ("B" in self.itemPressed)
                            and (h + dy >= minH)
                            and (gy - dy >= y + h - hScale)
                        ):
                            self.resize(self.width(), self.height() + dy)
                            # self.resize(w, h + dy)

    def checkLastwindow(self, windowType, windowDesignation):
        if (len(self.searchWindowdict) + len(self.globalSettingwindowDict) <= 1) and (
            windowType != "settingWindow"
        ):
            app.quit()
            return
        elif not len(self.searchWindowdict) + len(self.globalSettingwindowDict) <= 1:
            if (windowType == "infoWindow") or (windowType == "searchWindow"):
                settingsDict[windowDesignation]["searchWindow"] = {
                    "posX": self.searchWindowdict[windowDesignation].x(),
                    "posY": self.searchWindowdict[windowDesignation].y(),
                    "sizeX": self.searchWindowdict[windowDesignation].width(),
                    "sizeY": self.searchWindowdict[windowDesignation].height(),
                }
                settingsDict[windowDesignation]["infoWindow"] = {
                    "posX": self.infoWindowdict[windowDesignation].x(),
                    "posY": self.infoWindowdict[windowDesignation].y(),
                    "sizeX": self.infoWindowdict[windowDesignation].width(),
                    "sizeY": self.infoWindowdict[windowDesignation].height(),
                }
                self.searchWindowdict[windowDesignation].destroy()
                self.infoWindowdict[windowDesignation].destroy()
                self.searchWindowdict.pop(windowDesignation)
                self.infoWindowdict.pop(windowDesignation)
            if windowType == "globalSettingwindow":
                settingsDict[windowDesignation]["globalSettingwindow"] = {
                    "posX": self.globalSettingwindowDict[windowDesignation].x(),
                    "posY": self.globalSettingwindowDict[windowDesignation].y(),
                    "sizeX": self.globalSettingwindowDict[windowDesignation].width(),
                    "sizeY": self.globalSettingwindowDict[windowDesignation].height(),
                }
        if windowType == "settingWindow":
            if windowDesignation in self.settingWindowdict:
                settingsDict[windowDesignation]["settingWindow"] = {
                    "posX": self.settingWindowdict[windowDesignation].x(),
                    "posY": self.settingWindowdict[windowDesignation].y(),
                    "sizeX": self.settingWindowdict[windowDesignation].width(),
                    "sizeY": self.settingWindowdict[windowDesignation].height(),
                }
                self.windowTypes[windowType][windowDesignation].destroy()
                self.windowTypes[windowType].pop(windowDesignation)
                return
        elif (windowType != "infoWindow") and (windowType != "searchWindow"):
            self.windowTypes[windowType][windowDesignation].destroy()
            self.windowTypes[windowType].pop(windowDesignation)

    def closeAll(self):
        killList = []
        if not 0 in self.globalSettingwindowDict:
            self.globalSettingwindowDict[0] = globalSettingwindow(windowDesignation=0)
        for k in self.infoWindowdict:
            killList.append(k)
        for k in killList:
            self.checkLastwindow(
                self.infoWindowdict[k].__class__.__name__, self.infoWindowdict[k].windowDesignation
            )

    def drawBackground(self, painter):
        if "Background" in Media:
            painter.drawImage(QRect(0, 0, self.width(), self.height()), Media["Background"])
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 255))

    def updateWindows(self, windowList, windowDesignation):
        if windowList == "all":
            for k in self.windowTypes:
                for k2 in self.windowTypes[k]:
                    self.windowTypes[k][k2].update()
        else:
            for k in windowList:
                k[windowDesignation].update()

    def scaleResizer(self, target):
        target.dropMenu.dropListouterLayout.setContentsMargins(
            0, 5 * scaleFactor(), 0, 5 * scaleFactor()
        )
        target.dropMenu.dropListinnerLayout.setContentsMargins(
            0, 0, 5 * scaleFactor(), 5 * scaleFactor()
        )
        target.dropMenu.dropButton.setIconSize(QSize(16 * scaleFactor(), 16 * scaleFactor()))
        target.dropMenu.dropButton.setFixedSize(QSize(16 * scaleFactor(), 16 * scaleFactor()))
        for v in target.dropIcons:
            target.dropMenu.dropButtondict[v].setIconSize(
                QSize(45 * scaleFactor(), 20 * scaleFactor())
            )
            target.dropMenu.dropButtondict[v].setFixedSize(
                QSize(45 * scaleFactor(), 20 * scaleFactor())
            )
        if target.minimumHeight() < ((len(target.dropIcons) * 20) + 26) * scaleFactor():
            QTimer.singleShot(
                0,
                (
                    lambda: target.resize(
                        target.width(), (len(target.dropIcons) * 20 + 26) * scaleFactor()
                    )
                ),
            )
        else:
            QTimer.singleShot(0, (lambda: target.resize(target.width(), target.minimumHeight())))
        if target.minimumWidth() < 55 * scaleFactor():
            QTimer.singleShot(0, (lambda: target.resize(55 * scaleFactor(), target.height())))
        else:
            QTimer.singleShot(0, (lambda: target.resize(target.minimumWidth(), target.height())))
        QTimer.singleShot(0, (lambda: target.dropMenu.setSizePos()))

    def closeEvent(self, event):
        self.checkLastwindow(self.__class__.__name__, self.windowDesignation)
        event.ignore()

    def mousePressEvent(self, event):
        self.pressed = True
        if hasattr(self, "dropVis"):
            if self.dropVis:
                self.dropListToggle()
        pressPos = event.windowPos()
        self.checkFrame(pressPos)
        self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        releasePos = event.windowPos()
        self.pressed = False
        self.itemPressed = []
        self.DoubleClick = False
        self.update()

    def mouseMoveEvent(self, event):
        self.updateFrame(event)
        if hasattr(self, "dropMenu"):
            self.dropMenu.setSizePos()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Display Background
        self.drawBackground(painter)
        # Display Container
        self.drawContainer(painter)


class searchWindow(instanceWindow):
    def __init__(self, **kwargs):
        super().__init__(windowDesignation=kwargs["windowDesignation"])
        self.setMinimumSize(30, 30)
        self.DoubleClick = False
        self.linkedHighlight = False
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.loadWindowsettings()
        self.show()

    def mouseDoubleClickEvent(self, event):
        self.DoubleClick = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Display yellow see through.
        painter.fillRect(self.rect(), QColor(191, 161, 53, 60))
        # Show linked windows if double clicked
        self.drawLinked(painter)
        # Display Container
        self.drawContainer(painter)


class infoWindow(instanceWindow):
    dropIcons = ["NewIcon", "CloseIcon", "SettingIcon", "GlobalIcon", "CloseAllIcon"]
    itemInfo = None

    def __init__(self, **kwargs):
        super().__init__(windowDesignation=kwargs["windowDesignation"])
        self.setStyleSheet("QLabel{color: white;}")
        self.pressed = False
        self.itemPressed = []
        self.DoubleClick = False
        self.linkedHighlight = False
        self.trueOption = [0, 0, 0, 0, 0, 0, 0]
        self.loadWindowsettings()
        self.windowBox = QHBoxLayout()
        self.vBoxdict = {"main": QVBoxLayout(), "relic": QVBoxLayout(), "platinum": QVBoxLayout()}
        self.hBoxdict = {
            "relic": QHBoxLayout(),
            "platinum": QHBoxLayout(),
            "ducat": QHBoxLayout(),
            "efficency": QHBoxLayout(),
        }
        self.labelImagedict = {
            "relic": QLabel(self),
            "platinum": QLabel(self),
            "ducat": QLabel(self),
            "efficencyDucat": QLabel(self),
            "efficencyPlatinum": QLabel(self),
        }
        self.labelTextdict = {
            "relicItem": QLabel("Item:", self, Qt.AlignVCenter),
            "relicAccuracy": QLabel("Accuracy:", self, Qt.AlignVCenter),
            "platinumPrice": QLabel("Top plat:", self, Qt.AlignVCenter),
            "platinumAvg": QLabel("Top 10 Avg:", self, Qt.AlignVCenter),
            "ducatValue": QLabel("Ducats:", self, Qt.AlignVCenter),
            "efficencyValue": QLabel("Efficency:", self, Qt.AlignVCenter),
        }
        if settingsDict["listing"][0] == 0:
            self.labelTextdict["platinumPlayer"] = QLabel("Top Seller:", self, Qt.AlignVCenter)
        else:
            self.labelTextdict["platinumPlayer"] = QLabel("Top Buyer:", self, Qt.AlignVCenter)
        for k in self.vBoxdict:
            self.vBoxdict[k].setSpacing(2)
        for k in self.hBoxdict:
            self.hBoxdict[k].setSpacing(5)
        self.labelImagedict["relic"].setPixmap(Media["RelicIcon"])
        self.hBoxdict["relic"].addWidget(self.labelImagedict["relic"])
        # item
        self.vBoxdict["relic"].addWidget(self.labelTextdict["relicItem"])
        # accuracy
        self.vBoxdict["relic"].addWidget(self.labelTextdict["relicAccuracy"])
        self.hBoxdict["relic"].addLayout(self.vBoxdict["relic"])
        self.hBoxdict["relic"].addStretch(0)
        self.vBoxdict["main"].addLayout(self.hBoxdict["relic"])
        # platinum
        self.labelImagedict["platinum"].setPixmap(Media["PlatinumIcon"])
        self.hBoxdict["platinum"].addWidget(self.labelImagedict["platinum"])
        # seller
        self.vBoxdict["platinum"].addWidget(self.labelTextdict["platinumPlayer"])
        # top plat
        self.vBoxdict["platinum"].addWidget(self.labelTextdict["platinumPrice"])
        # top 10 avg
        self.vBoxdict["platinum"].addWidget(self.labelTextdict["platinumAvg"])
        self.hBoxdict["platinum"].addLayout(self.vBoxdict["platinum"])
        self.hBoxdict["platinum"].addStretch(0)
        self.vBoxdict["main"].addLayout(self.hBoxdict["platinum"])
        # ducat
        self.labelImagedict["ducat"].setPixmap(Media["DucatIcon"])
        self.hBoxdict["ducat"].addWidget(self.labelImagedict["ducat"])
        self.hBoxdict["ducat"].addWidget(self.labelTextdict["ducatValue"])
        self.hBoxdict["ducat"].addStretch(0)
        self.vBoxdict["main"].addLayout(self.hBoxdict["ducat"])
        # efficency
        self.labelImagedict["efficencyDucat"].setPixmap(Media["DucatIcon"])
        self.hBoxdict["efficency"].addWidget(self.labelImagedict["efficencyDucat"])
        self.labelImagedict["efficencyPlatinum"].setPixmap(Media["PlatinumIcon"])
        self.hBoxdict["efficency"].addWidget(self.labelImagedict["efficencyPlatinum"])
        self.hBoxdict["efficency"].addWidget(self.labelTextdict["efficencyValue"])
        self.hBoxdict["efficency"].addStretch(0)
        self.vBoxdict["main"].addLayout(self.hBoxdict["efficency"])
        self.vBoxdict["main"].addStretch(0)
        self.windowBox.addLayout(self.vBoxdict["main"])
        self.windowBox.addStretch(0)
        for tk, v in self.labelTextdict.items():
            v.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        for tk, v in self.labelImagedict.items():
            v.setScaledContents(1)
            v.setPixmap(QPixmap(24 * scaleFactor(), 24 * scaleFactor()))
            v.setFixedSize(24 * scaleFactor(), 24 * scaleFactor())
        self.dropMenu = dropConstructorclass(self)
        self.windowBox.setMargin(0)
        self.vBoxdict["main"].setMargin(10 * scaleFactor())
        self.setLayout(self.windowBox)
        self.updateDisplay()
        self.show()
        self.dropMenu.setSizePos()

    def updateDisplay(self):
        for Y in range(7):
            if settingsDict[self.windowDesignation]["radio"][Y] == 0:
                self.trueOption[Y] = settingsDict["globalRadio"][Y + 2]
            else:
                self.trueOption[Y] = settingsDict[self.windowDesignation]["radio"][Y] - 1
            for k in self.labelImagedict:
                self.labelImagedict[k].show()
        self.labelTextdict["relicItem"].setVisible(not self.trueOption[0])
        self.labelTextdict["relicAccuracy"].setVisible(not self.trueOption[1])
        self.labelTextdict["platinumPlayer"].setVisible(not self.trueOption[2])
        self.labelTextdict["platinumPrice"].setVisible(not self.trueOption[3])
        self.labelTextdict["platinumAvg"].setVisible(not self.trueOption[4])
        self.labelTextdict["ducatValue"].setVisible(not self.trueOption[5])
        self.labelTextdict["efficencyValue"].setVisible(not self.trueOption[6])
        if settingsDict["globalRadio"][1] == 1:
            self.hBoxdict["efficency"].setSpacing(0)
            for k in self.labelImagedict:
                self.labelImagedict[k].hide()
        elif settingsDict["globalRadio"][1] == 0:
            self.hBoxdict["efficency"].setSpacing(5)
            self.labelImagedict["relic"].setPixmap(Media["RelicIcon"])
            self.labelImagedict["platinum"].setPixmap(Media["PlatinumIcon"])
            self.labelImagedict["ducat"].setPixmap(Media["DucatIcon"])
            self.labelImagedict["efficencyDucat"].setPixmap(Media["DucatIcon"])
            self.labelImagedict["efficencyPlatinum"].setPixmap(Media["PlatinumIcon"])
            if self.trueOption[0] and self.trueOption[1]:
                self.labelImagedict["relic"].hide()
            elif not self.labelImagedict["relic"].isVisible():
                self.labelImagedict["relic"].show()
            if self.trueOption[2] and self.trueOption[3] and self.trueOption[4]:
                self.labelImagedict["platinum"].hide()
            elif not self.labelImagedict["platinum"].isVisible():
                self.labelImagedict["platinum"].show()
            if self.trueOption[5]:
                self.labelImagedict["ducat"].hide()
            elif not self.labelImagedict["ducat"].isVisible():
                self.labelImagedict["ducat"].show()
            if self.trueOption[6]:
                self.labelImagedict["efficencyDucat"].hide()
                self.labelImagedict["efficencyPlatinum"].hide()
            elif (
                not self.labelImagedict["efficencyDucat"].isVisible()
                and not self.labelImagedict["efficencyPlatinum"].isVisible()
            ):
                self.labelImagedict["efficencyDucat"].show()
                self.labelImagedict["efficencyPlatinum"].show()

    def mouseDoubleClickEvent(self, event):
        self.DoubleClick = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Display Background
        self.drawBackground(painter)
        # Show linked windows if double clicked
        self.drawLinked(painter)
        # Display Container
        self.drawContainer(painter)


class settingWindow(instanceWindow):
    dropIcons = ["CloseIcon", "GlobalIcon"]
    yOptions1 = [
        "Display Item",
        "Display Read Accuracy",
        "Display Top Seller",
        "Display Top Platinum",
        "Display Top 10 Avg",
        "Display Ducat",
        "Display Efficency",
    ]
    xOptions1 = ["Global", "On", "Off"]

    def __init__(self, **kwargs):
        super().__init__(windowDesignation=kwargs["windowDesignation"])
        self.setStyleSheet(
            "QRadioButton::indicator::unchecked {width: "
            + str(16 * scaleFactor())
            + "px; height: "
            + str(16 * scaleFactor())
            + "px;} QRadioButton::indicator::checked {width: "
            + str(16 * scaleFactor())
            + "px; height: "
            + str(16 * scaleFactor())
            + "px;} QLabel{color: white;}"
        )
        self.pressed = False
        self.itemPressed = []
        self.DoubleClick = False
        self.linkedHighlight = False
        self.loadWindowsettings()
        self.windowBox = QHBoxLayout()
        self.radioList = []
        self.radioList.append(
            radioConstructorclass(
                self, settingsDict[self.windowDesignation]["radio"], self.xOptions1, self.yOptions1
            )
        )
        for i, v in enumerate(self.radioList):
            self.windowBox.addLayout(self.radioList[i].radiobox)
            v.radiobox.setContentsMargins(10 * scaleFactor(), 0, 10 * scaleFactor(), 0)
        if len(self.radioList) == 1:
            self.radioList[0].radiobox.setMargin(10 * scaleFactor())
        else:
            self.radioList[0].radiobox.setContentsMargins(
                10 * scaleFactor(), 10 * scaleFactor(), 10 * scaleFactor(), 0
            )
            self.radioList[-1].radiobox.setContentsMargins(
                10 * scaleFactor(), 0, 10 * scaleFactor(), 10 * scaleFactor()
            )
        self.windowBox.addStretch(0)
        self.dropMenu = dropConstructorclass(self)
        self.windowBox.setMargin(0)
        self.setLayout(self.windowBox)
        self.show()
        self.dropMenu.setSizePos()

    def radioCheck(self, radioButton, Y, settingList):
        settingsDict[self.windowDesignation]["radio"][Y] = radioButton.group().checkedId()
        self.infoWindowdict[self.windowDesignation].updateDisplay()

    def mousePressEvent(self, event):
        if self.dropVis:
            self.dropListToggle()
        self.pressed = True
        pressPos = event.windowPos()
        self.itemPressed.append("Body")
        self.oldPos = event.globalPos()

    def mouseDoubleClickEvent(self, event):
        self.DoubleClick = True
        self.update()

    def scaleResizer(self, target):
        target.resize(target.minimumSize())

    def paintEvent(self, event):
        painter = QPainter(self)
        # Display Background
        self.drawBackground(painter)
        # Show linked windows if double clicked
        self.drawLinked(painter)
        # Display Container
        self.drawContainer(painter)


class globalSettingwindow(instanceWindow):
    yOptions1 = [
        "Load Background (Saves Memory)",
        "Show Icons",
        "Display Item",
        "Display Read Accuracy",
        "Display Top Seller",
        "Display Top Platinum",
        "Display Top 10 Avg",
        "Display Ducat",
        "Display Efficency",
    ]
    xOptions1 = ["On", "Off"]
    yOptions2 = ["Listings Shown"]
    xOptions2 = ["Sell", "Buy"]
    dropIcons = ["NewIcon", "CloseIcon", "CloseAllIcon", "QuitIcon", "ResetIcon"]

    def __init__(self, **kwargs):
        super().__init__(windowDesignation=kwargs["windowDesignation"])
        self.setStyleSheet(
            "QListView::item {height: "
            + str(16 * scaleFactor())
            + ";} QComboBox:editable {background-color: transparent; color: white; border-style: outset; border-width: "
            + str(1 * scaleFactor())
            + "px; border-radius: "
            + str(3 * scaleFactor())
            + "px; border-color: white;} QRadioButton::indicator::unchecked {width: "
            + str(16 * scaleFactor())
            + "px; height: "
            + str(16 * scaleFactor())
            + "px;} QRadioButton::indicator::checked {width: "
            + str(16 * scaleFactor())
            + "px; height: "
            + str(16 * scaleFactor())
            + "px;} QLabel{color: white;} QPushButton {background-color: transparent;}"
        )
        self.pressed = False
        self.itemPressed = []
        self.windowBox = QVBoxLayout()
        self.topSpacer = QSpacerItem(5 * scaleFactor(), 5 * scaleFactor())
        self.windowBox.addSpacerItem(self.topSpacer)
        # Saved Layouts
        self.savedLayoutsnames = []
        self.savedLayoutsInfo = QLabel("Saved Layouts", self, Qt.AlignVCenter)
        self.savedLayoutsInfo.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        self.savedLayoutsInfohBox = QHBoxLayout()
        self.savedLayoutsInfohBox.addStretch(0)
        self.savedLayoutsInfohBox.addWidget(self.savedLayoutsInfo)
        self.savedLayoutsInfohBox.addStretch(0)
        self.windowBox.addLayout(self.savedLayoutsInfohBox)
        self.savedLayoutsInfohBox.setContentsMargins(5 * scaleFactor(), 0, 0, 5 * scaleFactor())
        self.layoutsHbox = QHBoxLayout()
        self.layoutsLspacer = QSpacerItem(5 * scaleFactor(), 5 * scaleFactor())
        self.layoutsHbox.addSpacerItem(self.layoutsLspacer)
        self.savedLayoutscomboBox = QComboBox()
        self.savedLayoutscomboBox.setView(QListView())
        self.savedLayoutscomboBox.setLineEdit(QLineEdit())
        self.savedLayoutscomboBox.lineEdit().setPlaceholderText("New Layout")
        self.savedLayoutscomboBox.setInsertPolicy(QComboBox.NoInsert)
        self.savedLayoutscomboBox.view().setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        self.savedLayoutscomboBox.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        for k in list(layoutsDict.keys()):
            self.savedLayoutscomboBox.addItem(k)
        self.layoutsHbox.addWidget(self.savedLayoutscomboBox)
        self.savedLayoutscomboBox.setCurrentIndex(-1)
        self.layoutsRspacer = QSpacerItem(5 * scaleFactor(), 5 * scaleFactor())
        self.layoutsHbox.addSpacerItem(self.layoutsRspacer)
        self.windowBox.addLayout(self.layoutsHbox)
        self.savedLayoutsactionshBox = QHBoxLayout()
        self.savedLayoutsactions = {
            "Load": QPushButton(self, icon=Media["LoadLayouts"]),
            "Save": QPushButton(self, icon=Media["SaveLayouts"]),
            "Delete": QPushButton(self, icon=Media["DeleteLayouts"]),
        }
        self.savedLayoutsactionshBox.addStretch(0)
        for tk, v in self.savedLayoutsactions.items():
            self.savedLayoutsactionshBox.addWidget(v)
            self.savedLayoutsactionshBox.addStretch(0)
        self.windowBox.addLayout(self.savedLayoutsactionshBox)
        self.savedLayoutsactionshBox.setContentsMargins(0, 5 * scaleFactor(), 0, 5 * scaleFactor())
        for tk, v in self.savedLayoutsactions.items():
            v.setIconSize(QSize(45 * scaleFactor(), 20 * scaleFactor()))
            v.setFixedSize(QSize(45 * scaleFactor(), 20 * scaleFactor()))
        self.savedLayoutsactions["Save"].clicked.connect(self.saveLayout)
        self.savedLayoutsactions["Load"].clicked.connect(self.loadLayout)
        self.savedLayoutsactions["Delete"].clicked.connect(self.deleteLayout)
        # Radios
        self.radioList = []
        self.radioList.append(
            radioConstructorclass(self, settingsDict["globalRadio"], self.xOptions1, self.yOptions1)
        )
        self.radioList.append(
            radioConstructorclass(self, settingsDict["listing"], self.xOptions2, self.yOptions2)
        )
        for i, v in enumerate(self.radioList):
            self.windowBox.addLayout(self.radioList[i].radiobox)
            v.radiobox.setContentsMargins(10 * scaleFactor(), 0, 10 * scaleFactor(), 0)
        if len(self.radioList) == 1:
            self.radioList[0].radiobox.setMargin(10 * scaleFactor())
        else:
            self.radioList[0].radiobox.setContentsMargins(
                10 * scaleFactor(), 10 * scaleFactor(), 10 * scaleFactor(), 0
            )
            self.radioList[-1].radiobox.setContentsMargins(
                10 * scaleFactor(), 0, 10 * scaleFactor(), 10 * scaleFactor()
            )
        # Scale Slider
        self.sliderInfo = QLabel("UI Scale", self, Qt.AlignVCenter)
        self.sliderInfo.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        self.sliderInfohBox = QHBoxLayout()
        self.sliderInfohBox.addStretch(0)
        self.sliderInfohBox.addWidget(self.sliderInfo)
        self.sliderInfohBox.addStretch(0)
        self.windowBox.addLayout(self.sliderInfohBox)
        self.sliderInfohBox.setContentsMargins(0, 0, 0, 5 * scaleFactor())
        self.sliderHbox = QHBoxLayout()
        self.sliderLspacer = QSpacerItem(5 * scaleFactor(), 5 * scaleFactor())
        self.sliderHbox.addSpacerItem(self.sliderLspacer)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTracking(0)
        self.slider.setMinimum(0)
        self.slider.setMaximum(10)
        self.slider.setPageStep(1)
        self.slider.setValue(settingsDict["scale"][0])
        self.slider.valueChanged.connect(self.scaleChange)
        self.sliderHbox.addWidget(self.slider)
        self.sliderRspacer = QSpacerItem(5 * scaleFactor(), 5 * scaleFactor())
        self.sliderHbox.addSpacerItem(self.sliderRspacer)
        self.windowBox.addLayout(self.sliderHbox)
        self.sliderHbox.setContentsMargins(0, 0, 0, 5 * scaleFactor())
        self.windowBox.addStretch(0)
        # New and Info Buttons
        self.bottomButtonhBox = QHBoxLayout()
        self.bottomButtonhBox.addStretch(0)
        self.newButton = QPushButton(self, icon=Media["NewIconMain"])
        self.infoButton = QPushButton(self, icon=Media["InfoIcon"])
        self.newButton.setIconSize(QSize(90 * scaleFactor(), 40 * scaleFactor()))
        self.newButton.setFixedSize(QSize(90 * scaleFactor(), 40 * scaleFactor()))
        self.bottomButtonhBox.addWidget(self.newButton)
        self.bottomButtonhBox.addStretch(0)
        self.newButton.clicked.connect(self.newSearchwindow)
        self.infoButton.setIconSize(QSize(90 * scaleFactor(), 40 * scaleFactor()))
        self.infoButton.setFixedSize(QSize(90 * scaleFactor(), 40 * scaleFactor()))
        self.bottomButtonhBox.addWidget(self.infoButton)
        self.infoButton.clicked.connect(
            lambda: webbrowser.open(
                "https://github.com/JonathanSourdough/Warframe-Market-Overlay#warframe-market-overlay"
            )
        )
        self.bottomButtonhBox.addStretch(0)
        self.windowBox.addLayout(self.bottomButtonhBox)
        self.bottomButtonhBox.setContentsMargins(
            10 * scaleFactor(), 10 * scaleFactor(), 10 * scaleFactor(), 10 * scaleFactor()
        )
        self.windowBox.addStretch(0)
        # Wrap up
        self.dropMenu = dropConstructorclass(self)
        self.setLayout(self.windowBox)
        self.loadWindowsettings()
        self.show()
        self.dropMenu.setSizePos()
        self.dropMenu.lower()

    def saveLayout(self, *args):
        global settingsDict
        global layoutsDict
        currentText = self.savedLayoutscomboBox.currentText()
        self.savedLayoutsnames = []
        for i in range(self.savedLayoutscomboBox.count()):
            self.savedLayoutsnames.append(self.savedLayoutscomboBox.itemText(i))
        if currentText == "" or currentText == "" or currentText == "reset":
            return
        tempDict = {}
        for windowDesignation in self.searchWindowdict:
            if windowDesignation not in tempDict:
                tempDict[windowDesignation] = {}
            tempDict[windowDesignation]["searchWindow"] = {
                "posX": self.searchWindowdict[windowDesignation].x(),
                "posY": self.searchWindowdict[windowDesignation].y(),
                "sizeX": self.searchWindowdict[windowDesignation].width(),
                "sizeY": self.searchWindowdict[windowDesignation].height(),
            }
            tempDict[windowDesignation]["infoWindow"] = {
                "posX": self.infoWindowdict[windowDesignation].x(),
                "posY": self.infoWindowdict[windowDesignation].y(),
                "sizeX": self.infoWindowdict[windowDesignation].width(),
                "sizeY": self.infoWindowdict[windowDesignation].height(),
            }
            tempDict[windowDesignation]["radio"] = settingsDict[windowDesignation]["radio"]
        for windowDesignation in self.globalSettingwindowDict:
            if windowDesignation not in tempDict:
                tempDict[windowDesignation] = {}
            tempDict[windowDesignation]["globalSettingwindow"] = {
                "posX": self.globalSettingwindowDict[windowDesignation].x(),
                "posY": self.globalSettingwindowDict[windowDesignation].y(),
                "sizeX": self.globalSettingwindowDict[windowDesignation].width(),
                "sizeY": self.globalSettingwindowDict[windowDesignation].height(),
            }
        tempDict["globalRadio"] = settingsDict["globalRadio"]
        tempDict["listing"] = settingsDict["listing"]
        tempDict["scale"] = settingsDict["scale"]
        layoutsDict[currentText.lower()] = copy.deepcopy(tempDict)
        if not currentText in self.savedLayoutsnames:
            self.savedLayoutscomboBox.insertItem(2, currentText.lower())
        self.savedLayoutscomboBox.setCurrentIndex(-1)
        with open("layouts.p", "wb") as file:
            pickle.dump(layoutsDict, file, protocol=pickle.HIGHEST_PROTOCOL)

    def loadLayout(self, *args):
        global settingsDict
        global layoutsDict
        if self.savedLayoutscomboBox.currentIndex() != -1:
            self.closeAll()
            settingsDict = copy.deepcopy(
                layoutsDict[
                    self.savedLayoutscomboBox.itemText(self.savedLayoutscomboBox.currentIndex())
                ]
            )
            self.windowTypes["globalSettingwindow"][0].destroy()
            self.windowTypes["globalSettingwindow"].pop(0)
            self.savedLayoutscomboBox.setCurrentIndex(-1)
            for k, v in settingsDict.items():
                if "searchWindow" in v:
                    instance.searchWindowdict[k] = searchWindow(windowDesignation=k)
                    instance.infoWindowdict[k] = infoWindow(windowDesignation=k)
                if "globalSettingwindow" in v:
                    instance.globalSettingwindowDict[k] = globalSettingwindow(windowDesignation=k)
                if "settingWindow" in v:
                    instance.settingWindowdict[k] = settingWindow(windowDesignation=k)

    def deleteLayout(self, *args):
        global layoutsDict
        if (
            self.savedLayoutscomboBox.currentIndex() != -1
            and self.savedLayoutscomboBox.itemText(self.savedLayoutscomboBox.currentIndex())
            != "default"
            and self.savedLayoutscomboBox.itemText(self.savedLayoutscomboBox.currentIndex())
            != "reset"
        ):
            layoutsDict.pop(
                self.savedLayoutscomboBox.itemText(self.savedLayoutscomboBox.currentIndex())
            )
            self.savedLayoutscomboBox.removeItem(self.savedLayoutscomboBox.currentIndex())
            with open("layouts.p", "wb") as file:
                pickle.dump(layoutsDict, file, protocol=pickle.HIGHEST_PROTOCOL)
            self.savedLayoutscomboBox.setCurrentIndex(-1)

    def radioCheck(self, radioButton, Y, settingList):
        global cwd
        settingList[Y] = radioButton.group().checkedId()
        if settingList == settingsDict["globalRadio"]:
            if Y == 0:
                if (settingsDict["globalRadio"][0] == 1) and ("Background" in Media):
                    Media.pop("Background")
                    self.updateWindows("all", self.windowDesignation)
                elif (settingsDict["globalRadio"][0] == 0) and not ("Background" in Media):
                    Media["Background"] = QImage(cwd + r"\Media\Background.jpeg")
                    self.updateWindows("all", self.windowDesignation)
            if Y == 1:
                if settingsDict["globalRadio"][1] == 1:
                    for tk, v in self.infoWindowdict.items():
                        v.hBoxdict["efficency"].setSpacing(0)
                        for k in v.labelImagedict:
                            v.labelImagedict[k].hide()
                elif settingsDict["globalRadio"][1] == 0:
                    for tk, v in self.infoWindowdict.items():
                        v.hBoxdict["efficency"].setSpacing(5)
                        for k in v.labelImagedict:
                            v.labelImagedict[k].show()
                for tk, v in self.infoWindowdict.items():
                    QTimer.singleShot(0, (lambda: v.dropMenu.setSizePos()))
        elif settingList == settingsDict["listing"]:
            windows = []
            for k in self.infoWindowdict:
                windows.append(k)
            updateInfo(windows)
        for tk, v in self.infoWindowdict.items():
            v.updateDisplay()

    def scaleChange(self, scaleSlider):
        settingsDict["scale"][0] = scaleSlider
        self.topSpacer.changeSize(5 * scaleFactor(), 5 * scaleFactor())
        # Saved Layouts
        self.savedLayoutsInfo.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        self.savedLayoutsInfohBox.setContentsMargins(5 * scaleFactor(), 0, 0, 5 * scaleFactor())
        self.layoutsLspacer.changeSize(5 * scaleFactor(), 5 * scaleFactor())
        self.savedLayoutscomboBox.view().setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        self.savedLayoutscomboBox.lineEdit().setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        self.setStyleSheet(
            "QListView::item {height: "
            + str(16 * scaleFactor())
            + ";} QComboBox:editable {height: "
            + str(16 * scaleFactor())
            + "; color: white; background-color: transparent; border-style: outset; border-width: "
            + str(1 * scaleFactor())
            + "px; border-radius: "
            + str(3 * scaleFactor())
            + "px; border-color: white;} QRadioButton::indicator::unchecked {width: "
            + str(16 * scaleFactor())
            + "px; height: "
            + str(16 * scaleFactor())
            + "px;} QRadioButton::indicator::checked {width: "
            + str(16 * scaleFactor())
            + "px; height: "
            + str(16 * scaleFactor())
            + "px;} QLabel{color: white;} QPushButton {background-color: transparent;}"
        )
        self.layoutsRspacer.changeSize(5 * scaleFactor(), 5 * scaleFactor())
        for tk, v in self.savedLayoutsactions.items():
            v.setIconSize(QSize(45 * scaleFactor(), 20 * scaleFactor()))
            v.setFixedSize(QSize(45 * scaleFactor(), 20 * scaleFactor()))
        self.savedLayoutsactionshBox.setContentsMargins(0, 5 * scaleFactor(), 0, 5 * scaleFactor())
        # Radios
        for v in self.radioList:
            for sv in v.radioLabelslist:
                sv.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
            v.radiobox.setContentsMargins(10 * scaleFactor(), 0, 10 * scaleFactor(), 0)
        if len(v.radioList) == 1:
            self.radioList[0].radiobox.setMargin(10 * scaleFactor())
        else:
            self.radioList[0].radiobox.setContentsMargins(
                10 * scaleFactor(), 10 * scaleFactor(), 10 * scaleFactor(), 0
            )
            self.radioList[-1].radiobox.setContentsMargins(
                10 * scaleFactor(), 0, 10 * scaleFactor(), 10 * scaleFactor()
            )
        for k in self.radioList:
            for sk in k.radioLabelslist:
                k.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        QTimer.singleShot(0, lambda self=self: self.scaleResizer(self))
        # Scale Slider
        self.sliderInfo.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
        self.sliderInfohBox.setContentsMargins(0, 0, 0, 5 * scaleFactor())
        self.sliderLspacer.changeSize(5 * scaleFactor(), 5 * scaleFactor())
        self.sliderRspacer.changeSize(5 * scaleFactor(), 5 * scaleFactor())
        self.sliderHbox.setContentsMargins(0, 0, 0, 5 * scaleFactor())
        # Bottom Buttons
        self.newButton.setIconSize(QSize(90 * scaleFactor(), 40 * scaleFactor()))
        self.newButton.setFixedSize(QSize(90 * scaleFactor(), 40 * scaleFactor()))
        self.infoButton.setIconSize(QSize(90 * scaleFactor(), 40 * scaleFactor()))
        self.infoButton.setFixedSize(QSize(90 * scaleFactor(), 40 * scaleFactor()))
        self.bottomButtonhBox.setContentsMargins(
            10 * scaleFactor(), 10 * scaleFactor(), 10 * scaleFactor(), 10 * scaleFactor()
        )
        # Info Window
        for tk, v in self.infoWindowdict.items():
            for tk, sv in v.labelTextdict.items():
                sv.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
            for tk, sv in v.labelImagedict.items():
                sv.setPixmap(QPixmap(24 * scaleFactor(), 24 * scaleFactor()))
                sv.setFixedSize(24 * scaleFactor(), 24 * scaleFactor())
            v.vBoxdict["main"].setMargin(10 * scaleFactor())
            QTimer.singleShot(0, lambda v=v: self.scaleResizer(v))
        # Setting Window
        for tk, v in self.settingWindowdict.items():
            for sv in v.radioList:
                for tv in sv.radioLabelslist:
                    tv.setFont(QFont("Tahoma", 8 * scaleFactor(), 3))
            for sv in v.radioList:
                sv.radiobox.setContentsMargins(10 * scaleFactor(), 0, 10 * scaleFactor(), 0)
            if len(v.radioList) == 1:
                v.radioList[0].radiobox.setMargin(10 * scaleFactor())
            else:
                v.radioList[0].radiobox.setContentsMargins(
                    10 * scaleFactor(), 10 * scaleFactor(), 10 * scaleFactor(), 0
                )
                v.radioList[-1].radiobox.setContentsMargins(
                    10 * scaleFactor(), 0, 10 * scaleFactor(), 10 * scaleFactor()
                )
                v.setStyleSheet(
                    "QRadioButton::indicator::unchecked {width: "
                    + str(16 * scaleFactor())
                    + "px; height: "
                    + str(16 * scaleFactor())
                    + "px;} QRadioButton::indicator::checked {width: "
                    + str(16 * scaleFactor())
                    + "px; height: "
                    + str(16 * scaleFactor())
                    + "px;} QLabel{color: white;} QPushButton {background-color: transparent;}"
                )
            QTimer.singleShot(0, lambda v=v: self.scaleResizer(v))
        for k in self.infoWindowdict:
            self.infoWindowdict[k].updateDisplay()
        # Search Window
        for k in self.searchWindowdict:
            self.searchWindowdict[k].update()

    def mousePressEvent(self, event):
        if self.dropVis:
            self.dropListToggle()
        self.pressed = True
        pressPos = event.windowPos()
        self.itemPressed.append("Body")
        self.oldPos = event.globalPos()


def windowCreate():
    global instance
    instance = instanceWindow(windowDesignation=0)
    hk = SystemHotkey()
    hk.register(("control", "shift", "f"), callback=updateScan)
    hk.register(("control", "shift", "h"), callback=hideWindows)
    hk.register(("control", "shift", "h"), callback=instance.newSearchwindow)
    for k, v in settingsDict.items():
        if "searchWindow" in v:
            instance.searchWindowdict[k] = searchWindow(windowDesignation=k)
            instance.infoWindowdict[k] = infoWindow(windowDesignation=k)
        if "globalSettingwindow" in v:
            instance.globalSettingwindowDict[k] = globalSettingwindow(windowDesignation=k)
        if "settingWindow" in v:
            instance.settingWindowdict[k] = settingWindow(windowDesignation=k)
    ##listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
    ##listener.start()
    sys.exit(app.exec_())


def on_press(key):
    global current_keys
    # When a key is pressed, add it to the set we are keeping track of and check if this set is in the dictionary
    if key not in current_keys:
        current_keys.add(key)
    # print(current_keys)
    if frozenset(current_keys) in combinations:
        # If the current set of keys are in the mapping, execute the function
        combinations[frozenset(current_keys)]("")
        current_keys = set()


def on_release(key):
    # When a key is released, remove it from the set of keys we are keeping track of
    try:
        current_keys.remove(key)
    except:
        pass


if __name__ == "__main__":
    cwd = os.getcwd()
    Media = {}  # dictionary to hold onto all the media
    importantInfo = {}
    primePartsnames = []
    searchDefaults = {  # default search window settings
        "posX": 200,
        "posY": 440,
        "sizeX": 200,
        "sizeY": 65,
    }
    infoDefaults = {  # default info window settings
        "posX": 200,
        "posY": 300,
        "sizeX": 200,
        "sizeY": 140,
    }
    settingDefaults = {  # default settings window settings
        "posX": 400,
        "posY": 300,
        "sizeX": 230,
        "sizeY": 205,
    }
    globalSettingwindowdefaults = {  # default settings window settings
        "posX": 300,
        "posY": 500,
        "sizeX": 250,
        "sizeY": 250,
    }
    radioDefaults = [0, 0, 0, 0, 0, 0, 0]  # default settings window radio settings
    settingsDict = {}  # holds the current windows settings
    defaultDict = {
        "searchWindow": searchDefaults,
        "infoWindow": infoDefaults,
        "settingWindow": settingDefaults,
        "globalSettingwindow": globalSettingwindowdefaults,
        "radio": radioDefaults,
    }  # defaults when a new window is called
    layoutsDict = {  # all saved layouts dict
        "default": {
            "globalRadio": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "listing": [0],
            "scale": [0],
            0: {
                "radio": [0, 0, 0, 0, 0, 0, 0],
                "searchWindow": {"posX": 478, "posY": 398, "sizeX": 236, "sizeY": 67},
                "infoWindow": {"posX": 478, "posY": 78, "sizeX": 200, "sizeY": 145},
                "globalSettingwindow": {"posX": 94, "posY": 107, "sizeX": 261, "sizeY": 440},
            },
            1: {
                "searchWindow": {"posX": 721, "posY": 398, "sizeX": 236, "sizeY": 67},
                "radio": [0, 0, 0, 0, 0, 0, 0],
                "infoWindow": {"posX": 720, "posY": 78, "sizeX": 200, "sizeY": 145},
            },
            2: {
                "searchWindow": {"posX": 964, "posY": 398, "sizeX": 235, "sizeY": 67},
                "radio": [0, 0, 0, 0, 0, 0, 0],
                "infoWindow": {"posX": 963, "posY": 77, "sizeX": 200, "sizeY": 145},
            },
            3: {
                "searchWindow": {"posX": 1206, "posY": 398, "sizeX": 235, "sizeY": 66},
                "radio": [0, 0, 0, 0, 0, 0, 0],
                "infoWindow": {"posX": 1204, "posY": 77, "sizeX": 200, "sizeY": 145},
            },
        },
        "reset": {
            "globalRadio": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "listing": [0],
            "scale": [0],
            0: {"globalSettingwindow": {"posX": 94, "posY": 107, "sizeX": 261, "sizeY": 440}},
        },
    }
    try:  # tries to find the file the layouts saves to
        with open("layouts.p", "rb") as file:
            layoutsDict = pickle.load(file)
    except:  # if it cant do it, just use the earlier called out dict.
        pass
    settingsDict = copy.deepcopy(layoutsDict["default"])
    dropLoadnames = [
        "DropIcon",
        "DropDulledIcon",
        "NewIcon",
        "CloseIcon",
        "SettingIcon",
        "GlobalIcon",
        "MainIcon",
        "CloseAllIcon",
        "QuitIcon",
        "ResetIcon",
    ]  # load names for the drop menu
    frameLoadnames = ["HBar", "VBar", "TLCorner"]  # load names for the frame for all windows
    iconLoadnames = [
        "PlatinumIcon",
        "DucatIcon",
        "FormaIcon",
        "RelicIcon",
    ]  # load names for the info window icons
    mainLoadnames = ["NewIconMain", "InfoIcon"]  # load names for the main window
    radioLoadnames = ["RadioOffIcon", "RadioOnIcon"]  # load names for the radio buttons
    layoutsLoadnames = [
        "DefaultLayouts",
        "LoadLayouts",
        "SaveLayouts",
        "DeleteLayouts",
    ]  # load names for the global settings layouts loader
    # combinations = {
    #    frozenset(
    #        [
    #            pynput.keyboard.Key.ctrl_l,
    #            pynput.keyboard.Key.shift,
    #            pynput.keyboard.KeyCode(char="\x06"),
    #        ]
    #    ): updateScan,
    #    frozenset(
    #        [
    #            pynput.keyboard.Key.ctrl_l,
    #            pynput.keyboard.Key.shift,
    #            pynput.keyboard.KeyCode(char="\x08"),
    #        ]
    #    ): hideWindows,
    # }
    # current_keys = set()
    instance = None
    app = QApplication(sys.argv)
    loadMedia()
    windowCreate()
