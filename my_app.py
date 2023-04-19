# -*- coding: utf-8 -*-
# @Time : 2022/8/11 16:25
# @Author : tiger


import sys
import os

import json
import numpy as np
import pandas as pd
import cv2
import shutil

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from my_app_ui import Ui_MainWindow
from ensure_ui import Ui_ensure_window
from subsidence_ui import Ui_subsidence_window
from deformation_ui import Ui_deformation_window


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # initial child window
        self.ensure_window = EnsureWindow()
        self.subsidence_window = SubsidenceWindow()
        self.deformation_window = DeformationWindow()

        #
        self.file_path = ''  # 'E:/image_data_base'
        self.imgs = []  # image name with full path
        self.labs = []  # labels name with full path
        self.current_img = ''  # 'E:/image_data_base/imgs/xx.jpg'
        self.label_info = dict()  # {'key': 'value'}
        self.current_lab = ''  # 'E:/image_data_base/labs/xx.json'

        # open file
        self.actionopen.triggered.connect(self.open_msg)

        # prev image
        self.pushbutton_prev.clicked.connect(self.prev_img)
        # next image
        self.pushbutton_next.clicked.connect(self.next_img)

        # add label
        self.pushbutton_add_label.clicked.connect(self.add_label)

        # delete all label
        self.pushbutton_delete_all_label.clicked.connect(self.open_ensure_window)

        # delete one label
        self.pushbutton_delete_label.clicked.connect(self.delete_one_label)

        # turn to point image
        self.lineedit_turn_to_image.returnPressed.connect(self.turn_to_image)

        # open subsidence window
        self.pushbutton_subsidence.clicked.connect(self.open_subsidence_window)

        # open deformation window
        self.pushbutton_deformation.clicked.connect(self.open_deformation_window)

    def open_msg(self):
        """open data file
            structure: datafile
                        --imgs
                        --labels
        """
        self.file_path = QFileDialog.getExistingDirectory(self, "open", "C:/")
        self.statusbar.showMessage(self.file_path)

        # save image names
        try:
            # images
            img_names = os.listdir(os.path.join(self.file_path, 'imgs'))
            self.imgs = [os.path.join(self.file_path, 'imgs', img_name) for img_name in img_names]

            # labels
            self.get_labs_list()

        except Exception as e:
            print('file path is wrong!')

        # show images list
        self.current_img = self.imgs[0]
        self.show_images_list()

        # show images and labels
        self.show_img()
        self.show_labs_list_default()

    def get_labs_list(self):
        """get labs list in file:'labs' """
        lab_names = os.listdir(os.path.join(self.file_path, 'labs'))
        self.labs = [os.path.join(self.file_path, 'labs', lab_name) for lab_name in lab_names]

    def show_img(self):
        """show one image by current image path"""
        img = cv2.imread(self.current_img, 1)

        w_label, h_label = self.label.width(), self.label.height()
        canvas = letterbox_image(img, (w_label, h_label))

        q_img = cv2qimage(canvas)
        self.label.setPixmap(QPixmap.fromImage(q_img))

    def next_img(self):
        """change to next image"""
        if self.current_img == self.imgs[-1]:
            self.popwindow_last_img()
        else:
            current_index = self.imgs.index(self.current_img)
            self.current_img = self.imgs[current_index + 1]
            # show image and labels
            self.show_img()
            self.show_labs_list_default()

            # updata image list
            self.show_images_list()

    def prev_img(self):
        """change to prev image"""
        if self.current_img == self.imgs[0]:
            self.popwindow_first_img()
        else:
            current_index = self.imgs.index(self.current_img)
            self.current_img = self.imgs[current_index - 1]
            # show image and labels
            self.show_img()
            self.show_labs_list_default()

            # updata image list
            self.show_images_list()

    def turn_to_image(self):
        """show point image"""
        img_name = self.lineedit_turn_to_image.text()
        img = os.path.join(self.file_path, 'imgs', img_name)

        if img in self.imgs:
            self.current_img = img
            # show image and labels
            self.show_img()
            self.show_labs_list_default()

            # updata image list
            self.show_images_list()

        else:
            self.popwindow_img_not_exist()

        # clear lineedit of turn to image
        self.lineedit_turn_to_image.clear()

    def show_images_list(self):
        """show images name in textbrowser"""
        self.textbrowser_images.clear()
        cursor = self.textbrowser_images.textCursor()
        position = 0
        for img in self.imgs:
            if img == self.current_img:
                text = "<font size='5' color='red'>" + img.split('\\')[-1] + "<font>"
                self.textbrowser_images.append(text)
                position = cursor.position()
            else:
                label_name = img.split('\\')[-1][:-3] + 'json'
                lab = os.path.join(self.file_path, 'labs', label_name)

                if lab in self.labs:
                    text = "<font size='5' color='green'>" + img.split('\\')[-1] + "<font>"
                else:
                    text = "<font size='5' color='black'>" + img.split('\\')[-1] + "<font>"
                self.textbrowser_images.append(text)
        cursor.setPosition(position)
        self.textbrowser_images.setTextCursor(cursor)

    def show_labs_list_default(self):
        """show labels information in textbrowser"""
        label_name = self.current_img.split('\\')[-1][:-3] + 'json'
        self.current_lab = os.path.join(self.file_path, 'labs', label_name)

        self.textbrowser_labels.clear()
        if self.current_lab in self.labs:
            with open(self.current_lab, 'r') as f:
                self.label_info = json.load(f)
            self.updata_labs_list()
        else:
            self.label_info = dict()

    def updata_labs_list(self):
        """updata information in textbrowser, need label information dictionary"""
        self.textbrowser_labels.clear()
        for key, value in self.label_info.items():
            text = "<font size='4' color='black'>" + key + ': ' + value + "<font>"
            self.textbrowser_labels.append(text)

    def add_label(self):
        """add label for current image"""
        # check whether labels already exist
        key_get = str(self.lineedit_key.text())
        value_get = str(self.lineedit_value.text())

        # key and value are must not None
        if key_get and value_get:
            self.label_info[key_get] = value_get

            # updata labels textbrowser
            self.updata_labs_list()

            # save labels information to json
            self.save_label()

    def save_label(self):
        """save current label information"""
        with open(self.current_lab, 'w+') as f:
            json.dump(self.label_info, f)

        # updata label list
        self.get_labs_list()

    def delete_all(self, ensure_number):
        """delete all labels"""
        # close ensure window
        self.ensure_window.close()
        # if ensure window return yes
        if ensure_number:
            # check if label.json exist
            if os.path.isfile(self.current_lab):
                os.remove(self.current_lab)

                # empty self values
                self.label_info = dict()

                # updata labels list and total label files
                self.updata_labs_list()
                self.get_labs_list()

    def delete_one_label(self):
        """delete one label by key"""
        key_get = str(self.lineedit_delete_key.text())

        if key_get in self.label_info.keys():
            self.label_info.pop(key_get)
        # if label information is empty
        if not self.label_info:
            self.delete_all(1)

        # updata label list
        self.updata_labs_list()

    def open_ensure_window(self):
        """ensure if delete all labels"""
        self.ensure_window.ensure_signal.connect(self.delete_all)
        self.ensure_window.show()

    def open_subsidence_window(self):
        """open subsidence window, default file path is filepath/tables/subsidence.json"""
        self.subsidence_window.get_data(self.file_path)
        self.subsidence_window.show()

    def open_deformation_window(self):
        """open deformation window, default file path is filepath/tables/deformation.json"""
        self.deformation_window.get_data(self.file_path)
        self.deformation_window.show()

    def popwindow_first_img(self):
        """inform this is first image"""
        QMessageBox.information(self, "提示", "已经是第一张图片了")

    def popwindow_last_img(self):
        """inform this is last image"""
        QMessageBox.information(self, "提示", "已经是最后一张图片了")

    def popwindow_img_not_exist(self):
        """inform this image not exists"""
        QMessageBox.information(self, "提示", "输入的图片名称不存在")


class EnsureWindow(QMainWindow, Ui_ensure_window):
    ensure_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # click yes
        self.pushbutton_yes.clicked.connect(self.click_yes)

        # click no
        self.pushbutton_no.clicked.connect(self.click_no)

    # yes: delete all label
    def click_yes(self):
        self.ensure_signal.emit(1)

    def click_no(self):
        self.ensure_signal.emit(0)


class SubsidenceWindow(QMainWindow, Ui_subsidence_window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.file_path = ''  # excel's path
        self.data = dict()  # all data in excel, {index: [隧道id, 线路, 桩号, 沉降]}

        self.current_data = dict()  # current data showing in textbrowser
        self.conditions = ['', '', '', '']  # search conditions
        self.flag_find = True  # if search
        self.max_index = 0  # the max key of self.data

        # show data in textbrowsr when lineedit changed
        self.lineedit_1.textChanged.connect(self.search_data)
        self.lineedit_2.textChanged.connect(self.search_data)
        self.lineedit_3.textChanged.connect(self.search_data)
        self.lineedit_4.textChanged.connect(self.search_data)

        # add data
        self.pushbutton_add.clicked.connect(self.add_data)

        # delete data
        self.pushbutton_delete.clicked.connect(self.delete_data)

        # clear lineedit
        self.pushbutton_clear.clicked.connect(self.clear_linedit)

    def get_data(self, file_path):
        """"""
        # get subdsidence file's content
        self.file_path = os.path.join(file_path, 'tables', 'subsidence.json')
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.data = json.load(f)

        # # pandas to dict
        # for row in range(len(data)):
        #     self.data[row] = [str(data.iloc[row, 0]), str(data.iloc[row, 1]), str(data.iloc[row, 2]), str(data.iloc[row, 3])]

        # get max key
        self.max_index = len(self.data) - 1

        # show data
        self.current_data = self.data
        self.show_data()

    def show_data(self):
        """show data in textbrowser"""
        self.textBrowser.clear()
        # show how many data
        self.statusbar.showMessage('total: {} records'.format(len(self.current_data)))
        # show data
        for value in self.current_data.values():
            # text = value[0] + ' \t'*10 + value[1] + ' '*10 + value[2] + ' '*10 + value[3]
            # print(text)
            text = "<font size='5' color='red'>" + value[0] + "<font>"
            text = text + "<font size='5' color='blue'>" + " " + value[1] + "<font>"
            text = text + "<font size='5' color='green'>" + " " + value[2] + "<font>"
            text = text + "<font size='5' color='purple'>" + " " + value[3] + "<font>"
            self.textBrowser.append(text)

    def search_data(self):
        """search data"""
        self.conditions = [self.lineedit_1.text(), self.lineedit_2.text(), self.lineedit_3.text()]

        # flag_find
        self.flag_find = False
        # if condition is not null
        if any(self.conditions):
            search_data = []
            condition_index = []
            for i, condition in enumerate(self.conditions):
                if condition:
                    search_data.append(condition)
                    condition_index.append(i)

            self.current_data = dict()
            for key, value in self.data.items():
                match_data = []
                for index in condition_index:
                    match_data.append(value[index])
                if match_data == search_data:
                    self.current_data[key] = value
                    self.flag_find = True
        else:
            self.current_data = self.data

        # show data
        self.show_data()

    def add_data(self):
        """add data"""
        subsidence = self.lineedit_4.text()
        # if tunnel id,line,mile exist, use max to replace, but user decides
        if self.flag_find and len(self.current_data) == 1 and subsidence != '':
            for key in self.current_data.keys():
                self.data[key][-1] = subsidence
        else:
            # check if search condition is complete
            if len(self.current_data) == 0 and '' not in self.conditions and subsidence != '':
                add_data_tmp = self.conditions.copy()
                add_data_tmp.append(subsidence)
                self.max_index += 1
                self.data[self.max_index] = add_data_tmp
            else:
                QMessageBox.information(self, "提示", "输入信息不完整")

        # updata current data and show
        self.search_data()
        self.show_data()

        # save data
        self.save_data()

    def delete_data(self):
        """delete data"""
        if len(self.current_data) >= 1:
            for key in self.current_data.keys():
                del self.data[key]
        else:
            QMessageBox.information(self, "提示", "没有选中数据")

        # reset index
        data_tmp = dict()
        index = 0
        for key in self.data.keys():
            data_tmp[index] = self.data[key]
            index += 1

        self.data = data_tmp.copy()
        self.max_index = index - 1

        # updata current data and show
        self.search_data()
        self.show_data()

        # save data
        self.save_data()

    def clear_linedit(self):
        """clear all lineedit contents"""
        self.lineedit_1.clear()
        self.lineedit_2.clear()
        self.lineedit_3.clear()
        self.lineedit_4.clear()

    def save_data(self):
        """save data"""
        with open(self.file_path, 'w+') as f:
            f.write(json.dumps(self.data))


class DeformationWindow(QMainWindow, Ui_deformation_window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.file_path = ''  # excel's path
        self.data = dict()  # all data in excel, {index: [隧道id, 线路, 桩号, 变形]}

        self.current_data = dict()  # current data showing in textbrowser
        self.conditions = ['', '', '', '']  # search conditions
        self.flag_find = True  # if search
        self.max_index = 0  # the max key of self.data

        # show data in textbrowsr when lineedit changed
        self.lineedit_1.textChanged.connect(self.search_data)
        self.lineedit_2.textChanged.connect(self.search_data)
        self.lineedit_3.textChanged.connect(self.search_data)
        self.lineedit_4.textChanged.connect(self.search_data)

        # add data
        self.pushbutton_add.clicked.connect(self.add_data)

        # delete data
        self.pushbutton_delete.clicked.connect(self.delete_data)

        # clear lineedit
        self.pushbutton_clear.clicked.connect(self.clear_linedit)

    def get_data(self, file_path):
        """"""
        # get subdsidence file's content
        self.file_path = os.path.join(file_path, 'tables', 'deformation.json')
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.data = json.load(f)


        # # pandas to dict
        # for row in range(len(data)):
        #     self.data[row] = [str(data.iloc[row, 0]), str(data.iloc[row, 1]), str(data.iloc[row, 2]), str(data.iloc[row, 3])]

        # get max key
        self.max_index = len(self.data) - 1

        # show data
        self.current_data = self.data
        self.show_data()

    def show_data(self):
        """show data in textbrowser"""
        self.textBrowser.clear()
        # show how many data
        self.statusbar.showMessage('total: {} records'.format(len(self.current_data)))
        # show data
        for value in self.current_data.values():
            # text = value[0] + ' \t'*10 + value[1] + ' '*10 + value[2] + ' '*10 + value[3]
            # print(text)
            text = "<font size='5' color='red'>" + value[0] + "<font>"
            text = text + "<font size='5' color='blue'>" + " " + value[1] + "<font>"
            text = text + "<font size='5' color='green'>" + " " + value[2] + "<font>"
            text = text + "<font size='5' color='purple'>" + " " + value[3] + "<font>"
            self.textBrowser.append(text)

    def search_data(self):
        """search data"""
        self.conditions = [self.lineedit_1.text(), self.lineedit_2.text(), self.lineedit_3.text()]

        # flag_find
        self.flag_find = False
        # if condition is not null
        if any(self.conditions):
            search_data = []
            condition_index = []
            for i, condition in enumerate(self.conditions):
                if condition:
                    search_data.append(condition)
                    condition_index.append(i)

            self.current_data = dict()
            for key, value in self.data.items():
                match_data = []
                for index in condition_index:
                    match_data.append(value[index])
                if match_data == search_data:
                    self.current_data[key] = value
                    self.flag_find = True
        else:
            self.current_data = self.data

        # show data
        self.show_data()

    def add_data(self):
        """add data"""
        deformation = self.lineedit_4.text()
        # if tunnel id,line,mile exist, use max to replace, but user decides
        if self.flag_find and len(self.current_data) == 1 and deformation != '':
            for key in self.current_data.keys():
                self.data[key][-1] = deformation
        else:
            # check if search condition is complete
            if len(self.current_data) == 0 and '' not in self.conditions and deformation != '':
                add_data_tmp = self.conditions.copy()
                add_data_tmp.append(deformation)
                self.max_index += 1
                self.data[self.max_index] = add_data_tmp
            else:
                QMessageBox.information(self, "提示", "输入信息不完整")

        # updata current data and show
        self.search_data()
        self.show_data()

        # save data
        self.save_data()

    def delete_data(self):
        """delete data"""
        if len(self.current_data) >= 1:
            for key in self.current_data.keys():
                del self.data[key]
        else:
            QMessageBox.information(self, "提示", "没有选中数据")

        # reset index
        data_tmp = dict()
        index = 0
        for key in self.data.keys():
            data_tmp[index] = self.data[key]
            index += 1

        self.data = data_tmp.copy()
        self.max_index = index - 1

        # updata current data and show
        self.search_data()
        self.show_data()

        # save data
        self.save_data()

    def clear_linedit(self):
        """clear all lineedit contents"""
        self.lineedit_1.clear()
        self.lineedit_2.clear()
        self.lineedit_3.clear()
        self.lineedit_4.clear()

    def save_data(self):
        """save data"""
        with open(self.file_path, 'w+') as f:
            f.write(json.dumps(self.data))


def letterbox_image(img, inp_dim):
    """
    resize image to fit letterbox, keep image scale
    """
    img_w, img_h = img.shape[1], img.shape[0]
    w, h = inp_dim  # size of letterbox
    # 取min(w/img_w, h/img_h)这个比例来缩放，缩放后的尺寸为new_w, new_h,

    new_w = int(img_w * min(w / img_w, h / img_h))
    new_h = int(img_h * min(w / img_w, h / img_h))
    resized_image = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    # 将图片按照纵横比不变来缩放为new_w x new_h，768 x 576的图片缩放成416x312.,用了双三次插值
    # 创建一个画布, 将resized_image数据拷贝到画布中心。
    canvas = np.full((inp_dim[1], inp_dim[0], 3), 0)
    # 生成一个我们最终需要的图片尺寸h*w*3的array,这里生成416x416x3的array,每个元素值为0
    # 将wxhx3的array中对应new_wxnew_hx3的部分(这两个部分的中心应该对齐)赋值为刚刚由原图缩放得到的数
    canvas[(h - new_h) // 2:(h - new_h) // 2 + new_h, (w - new_w) // 2:(w - new_w) // 2 + new_w, :] = resized_image

    return np.array(canvas, dtype=np.uint8)


def cv2qimage(data):
    # 8-bits unsigned, NO. OF CHANNELS=1
    channels = 0
    if data.dtype == np.uint8:
        channels = 1 if len(data.shape) == 2 else data.shape[2]
    if channels == 3:  # CV_8UC3
        # Copy input Mat
        # Create QImage with same dimensions as input Mat
        img = QImage(data, data.shape[1], data.shape[0], data.strides[0], QImage.Format_RGB888)
        return img.rgbSwapped()
    elif channels == 1:
        # Copy input Mat
        # Create QImage with same dimensions as input Mat
        img = QImage(data, data.shape[1], data.shape[0], data.strides[0], QImage.Format_Indexed8)
        return img
    else:
        qDebug("ERROR: numpy.ndarray could not be converted to QImage. Channels = %d" % data.shape[2])
        return QImage()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_win = MyApp()
    my_win.show()
    sys.exit(app.exec_())
