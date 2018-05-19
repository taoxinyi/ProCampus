<!-- TOC -->

- [ProCampus](#procampus)
    - [1.1. Feature](#11-feature)
    - [1.2. How to Install](#12-how-to-install)
        - [1.2.1. Prerequisite](#121-prerequisite)
        - [1.2.2. install requirements](#122-install-requirements)
    - [1.3. Run](#13-run)
    - [Wired Thing](#wired-thing)

<!-- /TOC -->
# ProCampus
A forum featuring realtime chat, in combination of Django, WebSocket, Redis, Protobuf and more.
## 1.1. Feature
- Based on Django 2.0
- Using Django Channels in order to apply WebSocket for realtime chat and notifications, Redis as backend
    - Using Protobuf (Protocol buffers) as data structure between client and server, making the packet size significantly smaller compared to JSON.
- To be continued
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

    `git clone https://github.com/taoxinyi/Web.git`

## 1.3. Run
- go to folder

    `cd Web`

- start the server, then you can go to 127.0.0.1:8000
    `python3 manage.py runserver`



- if you want to access it not only from your  virtual machine, you can use below

    `python3 manage.py runserver 0.0.0.0:8000`

    Then you can use the ip from your virtual machine to test from host or mobile device in the same network.

    For instance, using `192.168.3.135:8000` in your host machine and` 127.0.0.1:8000` in virtual machine to test chat function.
## Wired Thing
When using [protobuf.min.js(protobuf.js)](https://github.com/dcodeIO/ProtoBuf.js), it is really wired that this library may convert underscore case into upper camel case refering to the `.proto` file.

 For instance, `chat_message_item` in `.proto` file may decoded as `chatMessageItem` in javascript.