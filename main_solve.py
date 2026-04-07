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
           AND  NOT EXISTS ( SELECT  *
                               FROM  ratings b
                              WHERE  b.user = {user}
                                AND  a.item = b.item
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
    query = f"""
    SELECT item, prediction
    FROM (
      SELECT item, ROUND(avg(std_rating), 4) as prediction
      FROM 
      (
        SELECT ratings.user, item, ROUND((rating-min_rating) / (max_rating-min_rating), 4) as std_rating
        FROM ratings 
        JOIN 
        (
            SELECT user, max(rating) as max_rating,
            CASE WHEN COUNT(rating)=1 THEN 0 ELSE min(rating) END as min_rating
            FROM ratings
            GROUP BY user
        ) tmp
        ON ratings.user=tmp.user
      ) std_ratings
      WHERE std_rating is not null
      GROUP BY item
    ) AS A
    WHERE NOT EXISTS (
        SELECT item 
        FROM ratings r
        WHERE user = {user} AND A.item = r.item AND rating is not null
    )
    ORDER BY prediction desc, item
    LIMIT {rec_num}
    """

    # 쿼리의 결과를 results 변수에 저장하세요.
    results = get_output(query)
    
    # 최종 결과 얻은 뒤, 중간 계산 중 만든 table 삭제
    # TODO end
    #=========================================================================

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

    #=========================================================================
    # TODO: remove sample, return actual recommendation result as df
    # YOUR CODE GOES HERE !
    # 쿼리의 결과를 results 변수에 저장하세요.
    # 아래가 기존 답안 

    query = f"""
        SELECT item, ROUND(sum(point), 4) as prediction
        FROM
        (
            SELECT user_2, item, std_sim*std_rating as point
            FROM
                (SELECT user_2, item, std_sim, std_rating
                    FROM 
                    (
                        WITH t1 AS
                        (
                            SELECT user_2, sim
                            FROM user_similarity u1
                            WHERE
                                u1.user_1 = {user}
                            ORDER BY u1.sim DESC, user_2 ASC
                            LIMIT 5
                        )
                        SELECT t1.user_2, t1.sim, ROUND(t1.sim/sum_sims.sum_sim, 4) as std_sim
                        FROM t1
                        CROSS JOIN
                        (
                            SELECT sum(sim) as sum_sim
                            FROM t1
                        )AS sum_sims
                    ) t2
                    JOIN 
                    (
                        SELECT ratings.user, item, ROUND((rating-min_rating) / (max_rating-min_rating), 4) as std_rating
                        FROM ratings 
                        JOIN 
                        (
                            SELECT user, max(rating) as max_rating,
                            CASE WHEN COUNT(rating)=1 THEN 0 ELSE min(rating) END as min_rating
                            FROM ratings
                            GROUP BY user
                        ) tmp
                        ON ratings.user=tmp.user
                    ) std_ratings
                    ON user=user_2
                ) AS A
        ) AS B
        WHERE NOT EXISTS (
            SELECT item 
            FROM ratings r
            WHERE user = {user} AND B.item = r.item AND rating is not null
        )
        GROUP BY item
        HAVING(prediction>{rec_num})
        ORDER BY prediction DESC, item ASC
    """
    results = get_output(query)

    #results = [(50 - x, x / 10) for x in range(50, math.ceil(rec_num * 10) - 1, -1)]
    # 최종 결과 얻은 뒤, 중간 계산 중 만든 table 삭제
    # TODO end
    #=========================================================================
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
    get_output("DROP TABLE IF EXISTS my_user_similarity")
    get_output("""
        CREATE TABLE my_user_similarity AS
        WITH UserNorms AS (
            -- 1. 각 유저별 벡터의 크기(L2 Norm)를 미리 계산
            SELECT  user
                  , SQRT(SUM(rating * rating)) AS norm
              FROM  ratings
             WHERE  rating > 0
             GROUP  BY user
        ),
        UserDotProduct AS (
            -- 2. 유저 간의 내적(Dot Product) 계산 (공통 아이템 기준)
            SELECT  a.user AS user_i
                  , b.user AS user_j
                  , SUM(a.rating * b.rating) AS dot_product
              FROM  ratings a
              JOIN  ratings b ON a.item = b.item
             GROUP  BY a.user, b.user
        )
        -- 3. 최종 유사도 계산 및 자기 자신 제외 처리
        SELECT  dp.user_i AS user_1
              , dp.user_j AS user_2
              , CASE 
                    WHEN dp.user_i = dp.user_j THEN 0 
                    ELSE ROUND(dp.dot_product / (ni.norm * nj.norm), 1) 
                END AS sim
          FROM  UserDotProduct dp
          JOIN  UserNorms ni ON dp.user_i = ni.user
          JOIN  UserNorms nj ON dp.user_j = nj.user;
    """)


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
                file_path = os.path.join(BASE_DIR, "prj.sql")
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
