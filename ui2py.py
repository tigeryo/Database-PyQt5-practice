# -*- coding: utf-8 -*-
# @Time : 2022/8/11 16:31
# @Author : tiger


import os
import os.path


dir = './'


def list_ui_file():
    list = []
    files = os.listdir(dir)
    for filename in files:
        if os.path.splitext(filename)[1] == '.ui':
            list.append(filename)

    return list


def trans_pyfile(filename):
    return os.path.splitext(filename)[0] + '.py'


def run_main():
    list = list_ui_file()
    for ui_file in list:
        pyfile = trans_pyfile(ui_file)
        cmd = 'pyuic5 -o {pyfile} {ui_file}'.format(pyfile=pyfile, ui_file=ui_file)
        os.system(cmd)


if __name__ == '__main__':
    run_main()