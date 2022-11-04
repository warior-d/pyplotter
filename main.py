from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QWidget, QApplication, \
    QAction, qApp, QPushButton, QDesktopWidget, QComboBox, QProgressBar, QLineEdit, \
    QSpacerItem, QVBoxLayout, QGroupBox
import os
from PyQt5 import uic
import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import sceletons
#from PyQt5 import QtWidgets


class Settings():
    URL_MANO = 'http://10.0.69.115/osm'
    API_TOKENS = '/admin/v1/tokens'
    API_VIM_ACCOUNTS = '/admin/v1/vim_accounts'
    API_CREATE_VNF = '/vnfpkgm/v1/vnf_packages_content'
    API_CREATE_NS = '/nsd/v1/ns_descriptors_content'
    API_CREATE_INSTANCE = '/nslcm/v1/ns_instances_content'
    API_DELETE_INSTANCE = '/nslcm/v1/ns_instances_content/'
    TOKEN = ''
    RAM_SIZES = ['1', '2', '3', '4']
    CPU_QNT = ['1', '2', '3', '4']
    STORAGE_SIZES = ['5', '10', '15', '20']
    IMAGES = ['Ubuntu 18.04', 'Ubuntu 20.04', 'CentOS 7', 'CentOS 8']
    OPENSTACK_IMAGES = {"Ubuntu 18.04" : "ubuntu18.04", "Ubuntu 20.04" : "ubuntu20.04", "CentOS 7" : "centos7", "Postgresql" : "postgres-image"}
    OPENSTACK_NETWORKS = ["shared", "public"]
    STATUS_VNF_CREATED, STATUS_NS_CREATED, STATUS_INSTANCE_CREATED = 201, 201, 201
    STATUS_NS_DELETE = 202
    STATU_TOKEN_CREATE = 200

class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('mainWidget.ui', self)
        self.header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json",
                  "Authorization": "Bearer " + Settings.TOKEN}
        self.vim_list = {}
        self.labelNameInstance.setText("Instance name: ")
        self.label_descr.setText("Description: ")
        self.label_image.setText("Image: ")
        self.label_ram.setText("RAM: ")
        self.label_cpu.setText("vCPU: ")
        self.label_storage.setText("Storage: ")
        self.label_network.setText("Network: ")
        self.label_vim.setText("Set VIM: ")
        self.pushButtonDelete.setVisible(False)
        self.getVims()
        self.fillCombos()
        self.comboBoxVims.currentTextChanged.connect(self.getVimIp)
        self.execBut.clicked.connect(self.execute)
        self.pushButtonDelete.clicked.connect(self.delete)
        self.base_vnf_ns_name = ''
        self.vnf_id = ''
        self.ns_id = ''
        self.service_id = ''
        self.progressBar.setValue(0)


    def getVims(self):
        url = Settings.URL_MANO + Settings.API_VIM_ACCOUNTS
        r = requests.get(url, headers=self.header)
        r.encoding
        jsonData = r.json()
        for item in jsonData:
            id = item['_id']
            name = item['name']
            type = item['vim_type']
            url = item["vim_url"]
            self.vim_list[name] = [id, type, url]

    def fillCombos(self):
        # VIM LIST
        vim_names = []
        for k in self.vim_list.keys():
            vim_names.append(k)
        self.comboBoxVims.addItems(vim_names)
        # RAM
        self.comboBoxRam.addItems(Settings.RAM_SIZES)
        # STORAGE
        self.comboBoxStorage.addItems(Settings.STORAGE_SIZES)
        # CPU
        self.comboBoxCpu.addItems(Settings.CPU_QNT)
        # Networks
        self.comboBoxNetwork.addItems(Settings.OPENSTACK_NETWORKS)
        # IMAGE
        image_name = []
        for k in Settings.OPENSTACK_IMAGES.keys():
            image_name.append(k)
        self.comboBoxImages.addItems(image_name)

    def getVimIp(self):
        curChek = self.comboBoxVims.currentText()
        ip = self.vim_list[curChek][2]
        self.labelIp.setText(ip)

    def deleteBtnVisual(self):
        if self.pushButtonDelete.isVisible():
            self.pushButtonDelete.setVisible(False)
        else:
            self.pushButtonDelete.setVisible(True)

    def execute(self):
        imageName = self.comboBoxImages.currentText()
        image = Settings.OPENSTACK_IMAGES[imageName]
        ram = self.comboBoxRam.currentText()
        vcpu = self.comboBoxCpu.currentText()
        storage = self.comboBoxStorage.currentText()
        network_name = self.comboBoxNetwork.currentText()
        self.base_vnf_ns_name = self.lineEdit.text()
        description = self.lineEditDescription.text()
        vimName = self.comboBoxVims.currentText()
        vimId = self.vim_list[vimName][0]
        header = {"Content-type": "text/plain",
                  "Accept": "application/json",
                  "Authorization": "Bearer " + Settings.TOKEN}
        if self.base_vnf_ns_name != '':
            #create VNFd
            vnf_id_name = self.base_vnf_ns_name + '_vnf'
            vnf = sceletons.createVnf(image, ram, vcpu, storage, vnf_id_name, description)
            # json.dumps() converts a dictionary to str object
            url = Settings.URL_MANO + Settings.API_CREATE_VNF
            # request to add VNFd
            r = requests.post(url, json=vnf, headers=header)
            jsonDataVnf = r.json()
            status = int(r.status_code)
            self.vnf_id = jsonDataVnf['id']
            print("VNF_ID: ", self.vnf_id)
            if(status == Settings.STATUS_VNF_CREATED):
                self.progressBar.setValue(1)
                # create NSd
                ns_id_name = self.base_vnf_ns_name + '_ns'
                ns = sceletons.createNs(ns_id_name, vnf_id_name, network_name, description)
                url = Settings.URL_MANO + Settings.API_CREATE_NS
                r = requests.post(url, json=ns, headers=header)
                jsonDataNs = r.json()
                status = int(r.status_code)
                print(status)
                self.ns_id = jsonDataNs['id']
                print("NS_ID: ", self.ns_id)
                if (status == Settings.STATUS_NS_CREATED):
                    self.progressBar.setValue(2)
                    # create service!
                    instance_name = self.base_vnf_ns_name
                    instance_description = description
                    ns_id = self.ns_id
                    vim_id = vimId
                    header = {"Content-type": "application/json",
                              "Accept": "application/json",
                              "Authorization": "Bearer " + Settings.TOKEN}
                    ns_create = sceletons.createInstance(instance_name, instance_description, ns_id, vim_id)
                    url = Settings.URL_MANO + Settings.API_CREATE_INSTANCE
                    print(ns_create)
                    r = requests.post(url, json=ns_create, headers=header)
                    jsonDataInstance = r.json()
                    status = int(r.status_code)
                    print(status)
                    try:
                        self.service_id = jsonDataInstance['id']
                    except Exception as e:
                        print(e)
                    if (status == Settings.STATUS_INSTANCE_CREATED):
                        self.progressBar.setValue(3)
                        self.deleteBtnVisual()
        else:
            print("Name instance!!!")


    def delete(self):
        header = {"Content-type": "application/json",
                  "Accept": "application/json",
                  "Authorization": "Bearer " + Settings.TOKEN}
        del_url = Settings.URL_MANO + Settings.API_DELETE_INSTANCE + self.service_id
        r = requests.delete(del_url, headers=header)
        status = int(r.status_code)
        if (status == Settings.STATUS_NS_DELETE):
            self.deleteBtnVisual()
            self.progressBar.setValue(0)
            self.lineEdit.setText('')
            self.lineEditDescription.setText('')
        


class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        uic.loadUi('dialog.ui', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.lineEditProject.setText("admin")
        self.lineEdit.setText("admin")
        self.lineEditPass.setText("admin")
        self.lineEditPass.setEchoMode(QLineEdit.Password)

    def handleLogin(self):
        flag = False
        login = self.lineEdit.text()
        password = self.lineEditPass.text()
        project = self.lineEditProject.text()
        url = Settings.URL_MANO + Settings.API_TOKENS
        post_fields = {'username': login, 'password': password, 'project_id': project}  # Set POST fields here
        header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        r = requests.post(url, data=urlencode(post_fields), headers=header)
        r.encoding
        jsonData = r.json()
        status = int(r.status_code)
        if status == Settings.STATU_TOKEN_CREATE:
            token = jsonData['_id']
            if len(token) > 10:
                flag = True
                Settings.TOKEN = token
                self.accept()
        if flag == False:
            self.labelInfo.setText("ошибка: "+ str(status))
        

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    login = Login()

    if login.exec_() == QDialog.Accepted:
        window = MainWidget()
        window.show()
        sys.exit(app.exec_())