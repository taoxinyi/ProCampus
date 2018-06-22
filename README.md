<!-- TOC -->

- [ProCampus](#procampus)
    - [1.1. Feature](#11-feature)
    - [1.2. How to Install](#12-how-to-install)
        - [1.2.1. Prerequisite](#121-prerequisite)
        - [1.2.2. install requirements](#122-install-requirements)
    - [1.3. Run](#13-run)
    - [1.4. Deployment](#14-deployment)
    - [1.5. Weird Thing](#15-weird-thing)
        - [1.5.1. Using protobuf.js](#151-using-protobufjs)
        - [Binary data corrupted during the transmission](#binary-data-corrupted-during-the-transmission)
    - [Acknowledgement](#acknowledgement)

<!-- /TOC -->
# ProCampus
A forum featuring realtime chat, comments and rating in combination of Django, WebSocket, Redis, Protobuf and more, compatible on mobile devices as well.

![Demo1](/screenshots/demo1.png "Demo1")

![Demo2](/screenshots/demo2.png "Demo2")

![Demo3](/screenshots/demo3.png "Demo3")

![Mobile Demo](/screenshots/mobile_demo.jpg "Mobile Demo")

## 1.1. Feature
- Based on Django 2.0
- Using Django Channels in order to apply WebSocket for realtime chat and notifications, Redis as backend
    - Using Protobuf (Protocol buffers) as data structure between client and server, making the packet size significantly smaller compared to JSON.
    - Featuring emoji and file sharing in the chatroom.
- Custom tags and comments in user info, featuring like and dislike

## 1.2. How to Install

### 1.2.1. Prerequisite
- Ubuntu has python3


### 1.2.2. install requirements
- Install python3 requirements

    `pip3 install -r requirements.txt --user`
- Using redis

    `docker run -p 6379:6379 -d redis:2.8`


    - you can use below to make sure it is on

         `netstat -ntlp|grep 6379`
- clone project

    `git clone https://github.com/taoxinyi/ProCampus.git`

## 1.3. Run
- go to folder

    `cd ProCampus`

- start the server, then you can go to 127.0.0.1:8000
    `python3 manage.py runserver`



- if you want to access it not only from your  virtual machine, you can use below

    `python3 manage.py runserver 0.0.0.0:8000`

    Then you can use the ip from your virtual machine to test from host or mobile device in the same network.

    For instance, using `192.168.3.135:8000` in your host machine and` 127.0.0.1:8000` in virtual machine to test chat function.

## 1.4. Deployment
Because of the usage of Websocket (`channels`), `daphne` should be used instead of `uwsgi` on server side when it comes to deployment.

- Install `nginx`

    `sudo apt-get install nginx`

- symlink nginx configuration

    ```
    cd /etc/nginx/sites-enabled/
    ln -s TheLocation/ProCampus/ProCampus.conf
    service nginx restart
    ```

- start `daphne`

    ```
    //if you want to see the log shown in shell
    daphne -b 0.0.0.0 -p 8800 ProCampus.asgi:application
    //if you don't want to see the log in shell but recorded
    nohup daphne -b 0.0.0.0 -p 8800 ProCampus.asgi:application &
    ```
- Start redis if you haven't do that yet

    `docker run -p 6379:6379 -d redis:2.8`

## 1.5. Weird Thing
### 1.5.1. Using protobuf.js
When using [protobuf.min.js(protobuf.js)](https://github.com/dcodeIO/ProtoBuf.js), it is really weird that this library may convert underscore case into lower camel case refering to the `.proto` file.

 For instance, `chat_message_item` as key in `.proto` file may decoded as `chatMessageItem` in Javascript.

 I almost know nothing about Javascript. If anyone knows the reason, please tell me.
 ### Binary data corrupted during the transmission
 Hard to tell it's the problem of `django channels`,`WebSocket` or `Transport layer`. The data transmitted to client browser is actually different from what is sent from server. This is really rare during regular chat, but somehow quite often when it comes to delivering file message to the client, especially when the file size>2MB.

 ## Acknowledgement
 - [Duan Yi (yumendy)](https://github.com/yumendy) for helping to build the base framwork and prototype in 2016
 - [lz7](https://github.com/lz7git) for helping to provide such a great emoji editor [`[easyEditor]`](https://github.com/lz7git/easyEditor)
 - other great libaries and framworks like `django`, `channels`, `UEditor`, `Redis`, `protobuf`, `protobuf.js`, etc.