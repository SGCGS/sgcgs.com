import requests
import re
import utility
import random
import json
import time
import _thread
import sqlite3
import threading
from contextlib import contextmanager
from fastapi.responses import PlainTextResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi import HTTPException
import utility


_local = threading.local()


@contextmanager
def acquire(*locks):
    locks = sorted(locks, key=lambda x: id(x))
    acquired = getattr(_local, 'acquired', [])
    if acquired and max(id(lock) for lock in acquired) >= id(locks[0]):
        raise RuntimeError('Lock Order Violation')
    acquired.extend(locks)
    _local.acquired = acquired
    try:
        for lock in locks:
            lock.acquire()
        yield
    finally:
        for lock in reversed(locks):
            lock.release()
        del acquired[-len(locks):]


class authorization:
    def __init__(self, dbp="./user.db", interval=900):
        self.interval = interval
        self.conn = sqlite3.connect(dbp, check_same_thread=False, timeout=5)
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS ACCOUNTS
           (USERNAME TEXT,
            PASSWORD TEXT,
            PERMISSION NUMBER,
            MANAGEBACID NUMBER);''')
        self.conn.commit()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS SESSIONS
           (COOKIE TEXT,
            USERNAME TEXT,
            CTIME NUMBER);''')
        self.conn.commit()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS MANAGEBACTOKENS
           (TOKEN TEXT,
            MANAGEBACID NUMBER,
            CTIME NUMBER);''')
        self.conn.commit()
        _thread.start_new_thread(self.expire, ())
        self.Lock = threading.Lock()

    def reCaptcha(self, token):
        payload = {
            "secret": utility.rsks,
            "response": token
        }
        r = requests.post(
            "https://recaptcha.net/recaptcha/api/siteverify", data=payload).json()
        if r["success"]:
            return True
        else:
            return False

    def randomToken(self):
        return ''.join(random.sample(
            "abcdefghijklmnopqrstuvwxyz1234567890", 36))

    def expire(self):
        while True:
            self.conn.execute(
                "DELETE FROM SESSIONS WHERE CTIME < ?", (int(time.time()) - self.interval,))
            self.conn.commit()
            self.conn.execute(
                "DELETE FROM MANAGEBACTOKENS WHERE CTIME < ?", (int(time.time()) - 300,))
            self.conn.commit()
            time.sleep(60)

    def getPermission(self, USERNAME, PASSWORD=None):
        with acquire(self.Lock):
            self.cur.execute(
                "SELECT * FROM ACCOUNTS WHERE USERNAME = ?", (USERNAME,))
            r = self.cur.fetchall()
        if r:
            if not PASSWORD == None:
                if PASSWORD == r[0][1]:
                    return r[0][2]
                else:
                    return 0
            else:
                return r[0][1]
        else:
            return 0

    def signUp(self, username, password, token, rt):
        if not self.reCaptcha(rt):
            raise HTTPException(status_code=401, detail="Robots go away")

        with acquire(self.Lock):
            self.cur.execute(
                "SELECT * FROM MANAGEBACTOKENS WHERE TOKEN = ?", (token,))
            r = self.cur.fetchall()
        if r:
            with acquire(self.Lock):
                self.cur.execute(
                    "SELECT * FROM ACCOUNTS WHERE USERNAME = ?", (username,))
                s = self.cur.fetchall()
            if not s:
                with acquire(self.Lock):
                    self.cur.execute(
                        "DELETE FROM MANAGEBACTOKENS WHERE TOKEN = ?", (token,))
                    self.conn.commit()
                    self.cur.execute(
                        "INSERT INTO ACCOUNTS VALUES(?, ?, ?, ?)", (username, password, 1, r[0][1],))
                    self.conn.commit()
                cookie = ''.join(random.sample(
                    "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+{}|-=[]\\:\";',./<>?", 50))
                with acquire(self.Lock):
                    self.cur.execute("INSERT INTO SESSIONS VALUES(?, ?, ?)",
                                     (cookie, username, int(time.time()), ))
                    self.conn.commit()
                r = PlainTextResponse()
                r.set_cookie("auth", cookie, self.interval, self.interval)
                return r
            else:
                raise HTTPException(
                    status_code=403, detail="Username already exists")
        else:
            raise HTTPException(
                status_code=401, detail="Invalid or expired token")

    def logIn(self, username, password, rt):
        if not self.reCaptcha(rt):
            raise HTTPException(status_code=401, detail="Robots go away")

        if self.getPermission(username, password):
            cookie = ''.join(random.sample(
                "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+{}|-=[]\\:\";',./<>?", 50))
            with acquire(self.Lock):
                self.cur.execute("INSERT INTO SESSIONS VALUES(?, ?, ?)",
                                 (cookie, username, int(time.time()), ))
                self.conn.commit()
            r = PlainTextResponse()
            r.set_cookie("auth", cookie, self.interval, self.interval)
            return r
        else:
            raise HTTPException(
                status_code=401, detail="Wrong password or username does not exist")

    def managebac(self, username, password, rt):
        if not self.reCaptcha(rt):
            raise HTTPException(status_code=401, detail="Robots go away")

        ua = utility.ua
        session = requests.Session()
        text = session.get("https://bgy.managebac.cn/login", headers=ua).text
        tmp = re.search(
            r"""<meta name="csrf-token" \/?[a-zA-Z]+("[^"]*"|'[^']*'|[^'">])*>""", text).group()
        tmp = tmp[tmp.find("content="):]
        authenticity_token = tmp[tmp.find("\"") + 1: tmp.rfind("\"")]
        payload = {
            "authenticity_token": authenticity_token,
            "login": username,
            "password": password,
            "remember_me": 0,
            "commit": "Sign-in"
        }
        r = session.post("https://bgy.managebac.cn/sessions",
                         data=payload, headers=ua)
        reditList = r.history
        cookie = session.cookies
        if reditList and reditList[len(reditList)-1].headers["location"] == "https://bgy.managebac.cn/student/home":
            token = self.randomToken()
            with acquire(self.Lock):
                self.cur.execute("INSERT INTO MANAGEBACTOKENS VALUES(?, ?, ?)",
                                 (token, cookie.get_dict()["user_id"], int(time.time()), ))
                self.conn.commit()
            return token
        else:
            raise HTTPException(
                status_code=401, detail="Wrong password or username does not exist")
