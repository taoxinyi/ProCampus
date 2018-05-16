# Web
## How to Install
### Prerequisite
- Ubuntu has python3
### install requirements
- install python3 requirements

    `pip3 install -r requirements.txt`

- using resdis

    `docker run -p 6379:6379 -d redis:2.8`


    - you can use below to make sure it is on
     `netstat -ntlp|grep 6379`
- clone project

    `git clone https://github.com/taoxinyi/Web.git`

- go to folder

    `cd Web`

- start the server, then you can go to 127.0.0.1:8000
    `python3 manage.py runserve`



#if you want to access it not only from your  virtual machine, you can use below
python3 manage.py runserver 0.0.0.0:8000```
