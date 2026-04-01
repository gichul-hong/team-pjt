#!/usr/bin/env python
# coding: utf-8

###################################################################
#                                                                 #
#   2026 DS2 Database Project : Recommendation using SQL-Python   #
#                                                                 #
###################################################################

import mysql.connector
from tabulate import tabulate
import pandas as pd
import math
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

## Connect to Remote Database
## Insert database information

HOST = "astronaut.snu.ac.kr"
USER = "DS2026_00038"
PASSWD = "DS2026_00038"
DB = "DS2026_00038"

connection = mysql.connector.connect(
    host=HOST,
    port=7000,
    user=USER,
    passwd=PASSWD,
    db=DB,
    autocommit=True,  # to create table permanently
)

cur = connection.cursor(dictionary=True)


## 수정할 필요 없는 함수입니다.
# DO NOT CHANGE INITIAL TABLES IN prj.sql
def get_dump(mysql_con, filename):
    """
    connect to mysql server using mysql_connector
    load .sql file (filename) to get queries that create tables in an existing database (fma)
    """
    query = ""
    try:
        with mysql_con.cursor() as cursor:
            for line in open(filename, "r"):
                if line.strip():
                    line = line.strip()
                    if line[-1] == ";":
                        query += line
                        cursor.execute(query)
                        query = ""
                    else:
                        query += line

    except Warning as warn:
        print(warn)
        sys.exit()


## 수정할 필요 없는 함수입니다.
# SQL query 를 받아 해당 query를 보내고 그 결과 값을 dataframe으로 저장해 return 해주는 함수
def get_output(query):
    cur.execute(query)
    out = cur.fetchall()
    df = pd.DataFrame(out)
    return df


# [Algorithm 1] Popularity-based Recommendation - 1 : Popularity by rating count
def popularity_based_count():
    user = int(input("User Id: "))
    rec_num = int(input("Number of recommendations?: "))

    print(f"Popularity Count based recommendation")
    print("=" * 99)

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 results 변수에 저장하세요.
    query = f"""
        SELECT  a.item AS item
              , COUNT(a.rating) AS prediction
          FROM  ratings a
         WHERE  1 = 1
           AND  a.item NOT IN ( SELECT  item
                                  FROM  ratings
                                 WHERE  user = {user}
                                   AND  rating IS NOT NULL ) 
           AND  a.rating IS NOT NULL
         GROUP  BY a.item
         ORDER  BY prediction DESC, a.item ASC
         LIMIT  {rec_num}
    """
    results = get_output(query)
    # 최종 결과 얻은 뒤, 중간 계산 중 만든 table 삭제
    # TODO end

    # Do not change this part
    # do not change column names
    df = pd.DataFrame(results, columns=["item", "prediction"])
    tab = tabulate(df, headers=df.columns, tablefmt="psql", showindex=False)
    print(tab)
    with open("pbc.txt", "w") as f:
        f.write(tab)
    print("Output printed in pbc.txt")


# [Algorithm 2] Popularity-based Recommendation - 2 : Popularity by average rating
def popularity_based_rating():
    user = int(input("User Id: "))
    rec_num = int(input("Number of recommendations?: "))

    print(f"Popularity Rating based recommendation")
    print("=" * 99)

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 results 변수에 저장하세요.
    query1 = f"""
        -- User 별 MIN / MAX 및 Count를 구한다. 여기서 평점이 없는 것들은 무시한다.
        DROP TABLE if EXISTS prob_2_1;
        CREATE TABLE prob_2_1 AS
        SELECT  user
              , CASE WHEN COUNT(rating) = 1 THEN 0 ELSE MIN(rating) END AS min_rating
              , MAX(rating) AS max_rating
              , COUNT(rating) AS cnt
          FROM  ratings
         WHERE  rating IS NOT NULL
         GROUP  BY user;
         
        -- User 별 보정Rating을 계산해서 임시 테이블에 적재
        DROP TABLE if EXISTS prob_2_2;
        CREATE TABLE prob_2_2 AS
        SELECT  a.user AS user
              , a.item AS item
              , ROUND((a.rating - b.min_rating) / (b.max_rating - b.min_rating), 4) AS adj_rating 
          FROM  ratings a
          JOIN  prob_2_1 b
            ON  a.user = b.user
         WHERE  a.rating IS NOT NULL;
        
        -- 보정된 점수를 기반으로 아이템 별 사용자가 부여한 평점의 평균 구하기
        DROP TABLE if EXISTS prob_2_3;
        CREATE TABLE prob_2_3 AS
        SELECT  item
              , ROUND(AVG(adj_rating), 4) AS avg_rating
          FROM  prob_2_2
         GROUP  BY item
         ;
    """
    get_output(query1)

    query2 = f"""
        SELECT  a.item AS item
              , avg_rating AS prediction
          FROM  prob_2_3 a
         WHERE  1 = 1
           AND  a.item NOT IN ( SELECT  item
                                  FROM  prob_2_2
                                 WHERE  user = {user} ) 
         ORDER  BY prediction DESC, a.item ASC
         LIMIT  {rec_num}
    """
    results = get_output(query2)
    
    # 최종 결과 얻은 뒤, 중간 계산 중 만든 table 삭제
    query3 = """
        DROP TABLE if EXISTS prob_2_1;
        DROP TABLE if EXISTS prob_2_2;
        DROP TABLE if EXISTS prob_2_3;
    """
    get_output(query3)
    # TODO end

    # Do not change this part
    # do not change column names
    df = pd.DataFrame(results, columns=["item", "prediction"])
    tab = tabulate(df, headers=df.columns, tablefmt="psql", showindex=False)
    print(tab)
    with open("pbr.txt", "w") as f:
        f.write(tab)
    print("Output printed in pbr.txt")


# [Algorithm 3] User-based Recommendation
def ubcf():
    user = int(input("User Id: "))
    rec_num = float(input("Recommendation Threshold: "))

    print("=" * 99)
    print(f"User-based Collaborative Filtering")
    print(f"Recommendations for user {user}")

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 results 변수에 저장하세요.
    results = [(50 - x, x / 10) for x in range(50, math.ceil(rec_num * 10) - 1, -1)]
    # 최종 결과 얻은 뒤, 중간 계산 중 만든 table 삭제
    # TODO end

    # Do not change this part
    # do not change column names
    df = pd.DataFrame(results, columns=["item", "prediction"])
    tab = tabulate(df, headers=df.columns, tablefmt="psql", showindex=False)
    print(tab)
    with open("ubcf.txt", "w") as f:
        f.write(tab)
    print("Output printed in ubcf.txt")


# [Algorithm 4] (Optional) User similarity
def user_similarity():

    print("=" * 99)
    print(f"User similarity")

    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !

    # 유사도 연산을 직접 구현하여 my_user_similarity 테이블에 저장하세요.
    df = get_output("SELECT * FROM my_user_similarity")
    # 최종 결과 얻은 뒤, 중간 계산 중 만든 table 삭제
    # TODO end

    # Do not change this part
    tab = tabulate(df, headers=df.columns, tablefmt="psql", showindex=False)
    # do not print since it is too large
    # print(tab)
    with open("user_similarity.txt", "w") as f:
        f.write(tab)
    print("Output printed in user_similarity.txt")


## 수정할 필요 없는 함수입니다.
# Print and execute menu
def menu():
    print("=" * 99)
    print("0. Initialize")
    print("1. Popularity Count-based Recommendation")
    print("2. Popularity Rating-based Recommendation")
    print("3. User-based Collaborative Filtering")
    print("4. User similarity (Optional)")
    print("5. Connector example")
    print("6. Exit database")
    print("=" * 99)

    while True:
        m = int(input("Select your action : "))
        if m < 0 or m > 6:
            print("Wrong input. Enter again.")
        else:
            return m


def execute():
    terminated = False
    while not terminated:
        m = menu()
        if m == 0:
            # 수정할 필요 없는 함수입니다.
            # Upload prj.sql before this
            # If autocommit=False, always execute after making cursor
            try:
                file_path = os.path.join(BASE_DIR, 'prj.sql')
                get_dump(connection, file_path)
                print("Database initialized successfully.")
            except:
                print("Error initializing database.")
        elif m == 1:
            popularity_based_count()
        elif m == 2:
            popularity_based_rating()
        elif m == 3:
            ubcf()
        elif m == 4:
            user_similarity()
        elif m == 5:
            # 수정할 필요 없는 함수입니다.
            # mysql connector 사용 방법 예시입니다.
            connector_example()
        elif m == 6:
            terminated = True


def connector_example():
    print("Connector example")
    print("=" * 99)
    rat_num = int(input("Number of rows in ratings?: "))
    sim_num = int(input("Number of rows in similarity?: "))

    query = f"SELECT * FROM ratings LIMIT {rat_num}"
    df = get_output(query)
    tab = tabulate(df, headers=df.columns, tablefmt="psql", showindex=False)
    print(tab)

    query = f"SELECT * FROM user_similarity LIMIT {sim_num}"
    df = get_output(query)
    tab = tabulate(df, headers=df.columns, tablefmt="psql", showindex=False)
    print(tab)

    query = "DROP TABLE IF EXISTS test;"
    df = get_output(query)

    query = "CREATE TABLE test AS SELECT * FROM ratings LIMIT 5;"
    df = get_output(query)

    query = "SELECT * FROM test;"
    df = get_output(query)
    tab = tabulate(df, headers=df.columns, tablefmt="psql", showindex=False)
    print(tab)

    query = "DROP TABLE test;"
    df = get_output(query)


# DO NOT CHANGE
if __name__ == "__main__":
    execute()
