# -*- coding: utf-8 -*-

import networkx as nx
import pymysql

HOST = '192.168.230.200'
PORT = 3307
USER = 'root'
PASSWD = '123'
DB = 'test'
CHARSET = 'utf8'


def init_mysql_connection():
    connection = pymysql.connect(host=HOST,
                                 port=PORT,
                                 user=USER,
                                 passwd=PASSWD,
                                 db=DB,
                                 charset=CHARSET)
    return connection


def select_sql(connection, sql):
    with connection.cursor() as cursor:
        sql = 'select * from test'
        cursor.execute(sql)
        results = cursor.fetchall()
        connection.commit()
    return results


def update_sql(connection, sql):
    with connection.cursor() as cursor:
        sql = "INSERT INTO test(username) VALUES (%s)"
        username = "Alex"
        # 执行SQL语句
        cursor.execute(sql, [username])
        # 提交事务
        connection.commit()


connection = init_mysql_connection()
update_sql(connection,"")
