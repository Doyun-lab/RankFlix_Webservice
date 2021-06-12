- [Project summary](#da-design-server)
  - [Purpose](#purpose)
  - [Requirements](#requirements)
  - [How to install](#how-to-install)
- [How to use](#how-to-use)
- [Version History](#version-history)
- [Contacts](#contacts)
- [License](#license)

---

### Project summary
넷플릭스 이용자들에게 데이터 기반 랭킹 및 콘텐츠 추천을 제공하는 웹 서비스를 개발한다.

#### Purpose
데이터아키텍처창의설계 수업 프로젝트 - server side 및 client side 개발

#### Requirements

* python >= 3.6.9
* flask >= 1.1.1, <= 1.1.2
* mongodb >= 3.6.3
* beautifulsoup4 >= 4.9.3
* selenium >= 3.141.0
* xlrd >= 2.0.1
* Google Chrome >= 91.0.4472.101

#### How to install

* Clone & Install

```sh
git clone https://github.com/Doyun-lab/da_design_server20181480
cd da_design_server_20181480
pip3 install -r requirements.txt
```

* Append two lines below to '~/.bashrc' file.

```sh
~$ cat >> ~/.bashrc
export DA_DESIGN_SERVER=/home/ubuntu/da_design_server20181480
export PYTHONPATH=$PYTHONPATH:$DA_DESIGN_SERVER
Ctrl+d

~$ source ~/.bashrc
```

---

### How to use

[Rank Flix](http://54.180.151.149:11100/)
위의 사이트에 접속하여 데이터 기반 랭킹 및 콘텐츠 추천을 받는다.

---

### Version History

* v.0.0.0 : 개발중

---

### Contacts

dy20181480@gmail.com

---

### License

Apache-2.0

![image](https://user-images.githubusercontent.com/70316401/118920316-2b126180-b971-11eb-8a4a-9ffd7f7334b3.png)
