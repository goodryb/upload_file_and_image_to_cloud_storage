#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import atexit
import datetime
import os
import sys
import configparser
from subprocess import call
import getpass

import oss2
from PyQt5.QtWidgets import QLabel, QTextEdit, QApplication, QLineEdit, QPushButton, QRadioButton, \
    QMainWindow, QFileDialog, QDesktopWidget
from qiniu import Auth, put_file, etag


class Example(QMainWindow):
    def __init__(self):
        super().__init__()

        self.GetFilePath = ""
        self.FilePath = ""
        self.initUI()

    def load_config(self):
        cf = configparser.ConfigParser()
        cf.read("config.ini")

        # 配置获取的模块
        try:
            self.oss_access_key_id = cf.get("oss", "access_key_id")
            self.oss_access_key_secret = cf.get("oss", "access_key_secret")
            self.oss_bucket_name = cf.get("oss", "bucket_name")
            self.oss_endpoint = cf.get("oss", "endpoint")
        except:
            self.oss.setDisabled(True)
            self.add_log("load oss config failed")

        try:
            self.quniu_access_key = cf.get("qiniu", "access_key")
            self.qiniu_secret_key = cf.get("qiniu", "secret_key")
            self.qiniu_bucket_name = cf.get("qiniu", "bucket_name")
            self.qiniu_get_file_path = cf.get("qiniu", "get_file_path")
        except:
            self.qiniu.setDisabled(True)
            self.add_log("load qiniu config failed")

        try:
            self.service_qiniu_default = cf.get("qiniu", "default")
            if self.qiniu.isEnabled() and self.service_qiniu_default == "0":
                self.qiniu.setChecked(True)
        except:
            pass

        if not self.qiniu.isChecked() and self.oss.isEnabled():
            self.oss.setChecked(True)
        else:
            self.qiniu.setChecked(True)

    def add_log(self, p_str):
        t_str = datetime.datetime.now().strftime('[%Y %m %d %H:%M:%S] ')
        self.qte.append(t_str + p_str)

    def file_select(self):
        file_path, filetype = QFileDialog.getOpenFileName(self, "选取文件",
                                                          "/Users/{0}/Downloads".format(getpass.getuser()))
        self.FilePath = file_path
        self.qle.setText(file_path.split("/")[-1])
        self.add_log('File select success ' + file_path)
        return True

    def capture(self):
        """
        从剪贴板生成图片
        :return: up_file_path， up_file_name
        """
        pngpaste = "/usr/local/bin/pngpaste"
        try:
            call([pngpaste, '-v'], stderr=open('/dev/null', 'w'))
        except OSError:
            self.add_log('please pre-install pngpaste use `brew install pngpaste` before use this script')
            return False

        up_file_name = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S.png')
        up_file_path = os.path.join('/tmp', up_file_name)
        atexit.register(lambda x: os.remove(x) if os.path.exists(x) else None, up_file_path)
        save = call([pngpaste, up_file_path])
        if save == 1:
            self.add_log('No image data found on the clipboard, or could not convert!')
            return False
        else:
            self.FilePath = up_file_path
            self.qle.setText(up_file_name)
            self.add_log(self.FilePath)
            return True

    def jietu(self):
        return self.capture()

    def oss_upload(self):
        file_path = self.FilePath
        FileName = file_path.split("/")[-1]
        bucket = oss2.Bucket(oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret), self.oss_endpoint,
                             self.oss_bucket_name)
        bucket.put_object_from_file(FileName, file_path)
        region = self.oss_endpoint.split("/")[2]
        ret = "https://{0}.{1}/{2}".format(self.oss_bucket_name, region, FileName)
        self.GetFilePath = ret
        self.add_log('OSS File upload success ' + ret)
        self.copytext()

    def qiniu_upload(self):

        # 构建鉴权对象
        q = Auth(self.quniu_access_key, self.qiniu_secret_key)
        # 要上传的空间
        bucket_name = self.qiniu_bucket_name

        # 上传到七牛后保存的文件名
        file_path = self.FilePath
        key = file_path.split("/")[-1]

        # 生成上传 Token，可以指定过期时间
        token = q.upload_token(bucket_name, key, 3600)

        # 更新状态栏
        self.add_log('File uploading')

        ret, info = put_file(token, key, file_path)

        assert ret['key'] == key
        assert ret['hash'] == etag(file_path)

        self.GetFilePath = self.qiniu_get_file_path + key
        self.add_log('Qiniu File upload success ' + self.GetFilePath)
        self.copytext()

    def copy_markdown_url(self):
        clipboard = QApplication.clipboard()
        if self.qle.text() != "":
            clipboard.setText("![](" + self.GetFilePath + ")")
            self.add_log('MarkDown url copy success ' + "![](" + self.GetFilePath + ")")
            return True
        else:
            self.add_log('No url !~~')
            return False

    def copytext(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.GetFilePath)
        self.add_log('http url copy success')

    def upload(self):

        if self.FilePath == "":
            self.add_log('No file select')
            return False

        if self.qiniu.isChecked() and self.qiniu.isEnabled():
            self.qiniu_upload()
        elif self.oss.isChecked() and self.oss.isEnabled():
            self.oss_upload()
        else:
            self.add_log("The select service is disabled, can not upload,check config.ini")
            return False

    def initUI(self):

        # 选择文件

        btn = QPushButton('选择文件', self)
        btn.setToolTip('选择要上传的图片文件')
        btn.resize(btn.sizeHint())
        btn.move(20, 10)
        btn.clicked.connect(self.file_select)

        # 文件路径
        fp = QLabel("文件名称", self)
        fp.move(20, 80)

        self.qle = QLineEdit(self)
        self.qle.setReadOnly(True)
        self.qle.setFixedWidth(270)
        self.qle.move(80, 80)

        # 服务商选择按钮
        self.qiniu = QRadioButton("七牛", self)
        self.qiniu.setToolTip("上传到七牛")
        self.oss = QRadioButton("OSS", self)
        self.oss.setToolTip("上传到阿里云OSS")

        self.oss.move(25, 40)
        self.qiniu.move(125, 40)

        # 截图上传
        self.cb = QPushButton("截图上传", self)
        self.cb.setToolTip("选中会自动从剪贴板读取截图，以便上传")
        self.cb.resize(115, 35)
        self.cb.move(225, 40)
        self.cb.clicked.connect(self.jietu)

        # 复制按钮
        cbtn = QPushButton("复制MD链接", self)
        cbtn.setToolTip("复制上一个上传成功的图片Markdown链接")
        cbtn.resize(cbtn.sizeHint())
        cbtn.move(225, 10)
        cbtn.clicked.connect(self.copy_markdown_url)

        # 上传按钮
        ubtn = QPushButton("开始上传", self)
        ubtn.setToolTip("根据选择的文件和服务商上传图片，上传成功后会自动复制URL到剪贴板")
        ubtn.resize(ubtn.sizeHint())
        ubtn.move(120, 10)
        ubtn.clicked.connect(self.upload)

        # 日志区域
        self.qte = QTextEdit(self)
        self.qte.move(20, 120)
        self.qte.setFixedWidth(330)
        self.qte.setFixedHeight(300)
        self.qte.setReadOnly(True)
        self.qte.setText("日志信息:")

        # 绘制窗口
        self.setFixedSize(370, 440)

        # 窗口居中
        self.frameGeometry().moveCenter(QDesktopWidget().availableGeometry().center())

        self.setWindowTitle('File Upload')
        self.show()
        self.load_config()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
