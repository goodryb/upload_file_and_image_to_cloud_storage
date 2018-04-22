## 主要功能
* 上传本地文件到云存储（七牛、阿里云OSS）
* 获取剪贴板图片，上传到云存储
* 生成URL或markdown链接

## 前置依赖

* pngpaste 用于获取剪贴板图片，可通过 "brew install pngpaste" 安装
* oss2 阿里云SDK，可通过 "pip install oss2" 安装
* qiniu  七牛SDK，可通过 "pip install qiniu" 安装

## 配置文件

复制example.config.ini 为 config.ini，填写认证信息
```
[oss]
access_key_id = ${oss_id}
access_key_secret = ${oss_secret}
bucket_name = ${oss_bucket_name}
endpoint = ${oss_endpoint}
;default service 0, otherwise not 0
default = 1


[qiniu]
access_key = ${qiniu_id}
secret_key = ${qiniu_secret}
bucket_name = ${qiniu_bucket_name}
get_file_path = ${qiniu_connect_url}
default = 0
```

## 使用方法
```
chmod +x upload.py
python3 upload.py
```

## 界面预览

![](http://7xqpyi.com1.z0.glb.clouddn.com/2018_04_22_10_17_32.png)

### 文件上传

1. 点击选择文件，打开要上传的文件
2. 选择要上传的云平台
3. 点击开始上传

### 图片上传
1. 使用任意工具截图
2. 选中截图上传
3. 选择要上传的云平台
4. 点击开始上传

上传完成后，自动复制URL到剪贴板，如需复制markdown格式，点击复制MD链接

## 支持平台
* Mac
