<!-- TOC -->

- [1. Web](#1-web)
    - [1.1. How to Install](#11-how-to-install)
        - [1.1.1. Prerequisite](#111-prerequisite)
        - [1.1.2. install requirements](#112-install-requirements)
        - [1.1.3. Run](#113-run)

<!-- /TOC -->
# 1. Web
## 1.1. How to Install
### 1.1.1. Prerequisite
- Ubuntu has python3
### 1.1.2. install requirements
- install python3 requirements

    `pip3 install -r requirements.txt`

- using resdis

    `docker run -p 6379:6379 -d redis:2.8`


    - you can use below to make sure it is on
     `netstat -ntlp|grep 6379`
- clone project

    `git clone https://github.com/taoxinyi/Web.git`

### 1.1.3. Run
- go to folder

    `cd Web`

- start the server, then you can go to 127.0.0.1:8000
    `python3 manage.py runserver`



- if you want to access it not only from your  virtual machine, you can use below

    `python3 manage.py runserver 0.0.0.0:8000`

    Then you can use the ip from your virtual machine to test from host or mobile device in the same network.

    For instance, using `192.168.3.135:8000` in your host machine and` 127.0.0.1:8000` in virtual machine to test chat function.
