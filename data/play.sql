COMMIT

ratings
user_similarity



# 
SELECT  COUNT(DISTINCT a.user)
      , COUNT(DISTINCT a.item)
  FROM  ratings a
-- 292ppl, 454 Items
;

-- NULL 이 있으니 주의해야 함
SELECT  COUNT(*) 
  FROM  ratings
 WHERE  rating IS NULL
-- 98232
; 

-- data preview
SELECT  a.user
      , COUNT(a.rating)
  FROM  ratings a
 WHERE  rating IS NOT NULL
 GROUP  BY a.user
 ORDER  BY 2 DESC
;

SELECT  a.item
      , COUNT(a.rating)
  FROM  ratings a
 GROUP  BY a.item
 ORDER  BY 1 

 
-- 0	56
-- 1	106
-- 2	76
-- 3	60
-- 4	86
-- 5	406

SELECT  a.item
      , COUNT(a.rating) AS cnt
  FROM  ratings a
 WHERE  1 = 1
   AND  NOT EXISTS ( SELECT  *
                       FROM  ratings
                      WHERE  1 = 1
                        AND  a.user = 222
                        AND  item = a.item ) 
 GROUP  BY a.item
 ORDER  BY cnt DESC, a.item ASC
 LIMIT  10
;
-- #1
SELECT  a.item
      , COUNT(a.rating) AS cnt
  FROM  ratings a
 WHERE  1 = 1
   AND  a.item NOT IN ( SELECT  item
                          FROM  ratings
                         WHERE  user = 222
                           AND  rating IS NOT NULL ) 
   AND  a.rating IS NOT NULL
 GROUP  BY a.item
 ORDER  BY cnt DESC, a.item ASC
 LIMIT  10 
;




-- #2 데이터 보기
SELECT  user
      , MIN(rating) AS min_rating
      , MAX(rating) AS max_rating
      , COUNT(rating) AS cnt
  FROM  ratings
 WHERE  rating IS NOT NULL
 GROUP  BY user
;

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
 
        SELECT  a.item AS item
              , avg_rating AS prediction
          FROM  prob_2_3 a
         WHERE  1 = 1
           AND  a.item NOT IN ( SELECT  item
                                  FROM  prob_2_2
                                 WHERE  user = {user} ) 
         ORDER  BY prediction DESC, a.item ASC
         LIMIT  {rec_num}




-- #3
-- 사용자 별 평점을 보정하여 prob_3_2에 넣어준다. 
DROP TABLE if EXISTS prob_3_1;
CREATE TABLE prob_3_1 AS
SELECT  user
      , CASE WHEN COUNT(rating) = 1 THEN 0 ELSE MIN(rating) END AS min_rating
      , MAX(rating) AS max_rating
      , COUNT(rating) AS cnt
  FROM  ratings
 WHERE  rating IS NOT NULL
 GROUP  BY user;
 
-- User 별 보정Rating을 계산해서 임시 테이블에 적재
DROP TABLE if EXISTS prob_3_2;
CREATE TABLE prob_3_2 AS
SELECT  a.user AS user
      , a.item AS item
      , ROUND((a.rating - b.min_rating) / (b.max_rating - b.min_rating), 4) AS adj_rating 
  FROM  ratings a
  JOIN  prob_3_1 b
    ON  a.user = b.user
 WHERE  a.rating IS NOT NULL;

-- 사용자 별로 가장 유사도가 높은 이웃 K명을 구한다. 유사도가 같을 경우 번호가 작은 사용자를 우선한다. 
-- 가장 similar 한 5명을 구한다. 
DROP TABLE IF EXISTS prob_3_3;
CREATE TABLE prob_3_3 AS
SELECT  a.user_2
      , a.sim
  FROM  user_similarity a
 WHERE  user_1 = 220
   AND  user_1 != user_2
 ORDER  BY a.sim DESC, a.user_2 ASC
 LIMIT  5
;

-- 각 사용자마다 계산된 유사도를 해당 사용자의 유사도의 총합으로 나누어 준다.
-- 나누어진 유사도는 소수점 넷째 자리까지 반올림한다.
UPDATE  prob_3_3 a
CROSS  JOIN ( SELECT  SUM(sim) AS total_sum 
                FROM  prob_3_3
            ) b
SET a.sim = ROUND(a.sim / b.total_sum, 4);
COMMIT
-- 행렬곱을 구한다. 여기서는 [1*5] 행렬과 [5*n]의 곱을 계산해야 한다. (n 은 아이템의 개수)
DROP TABLE IF EXISTS prob_3_4;
CREATE TABLE prob_3_4 AS
SELECT  b.item
      , ROUND(SUM(a.sim * b.adj_rating), 4) AS prediction
  FROM  prob_3_3 a
  JOIN  prob_3_2 b
    ON  a.user_2 = b.user
 GROUP  BY b.item
;

        SELECT  a.item AS item
              , avg_rating AS prediction
          FROM  prob_3_4 a
         WHERE  1 = 1
           AND  a.prediction >= {rec_num}
           AND  a.item NOT IN ( SELECT  item
                                  FROM  prob_3_2
                                 WHERE  user = {user} ) 
         ORDER  BY a.prediction DESC, a.item ASC
         LIMIT  {rec_num}



-- #4
-- calculate AA^T
DROP TABLE IF EXISTS prob_4_1;
CREATE  TABLE prob_4_1 AS
SELECT  a.user AS user_i       -- 행렬 A의 사용자 (Row)
      , b.user AS user_j       -- 전치 행렬 B의 사용자 (Column)
      , SUM(a.rating * b.rating) AS dot_product
  FROM  ratings a
  JOIN  ratings b 
    ON  a.item = b.item 
 GROUP  BY  a.user, b.user; 
-- Script execution finished
-- Total script execution time: 24.35s

-- 이것은 중복이 있으다. 상삼각만 있으면 되긴함..
-- SELECT * FROM prob_4_1
--  WHERE  (user_i = 1 AND user_j = 33) OR (user_i = 33 AND user_j = 1)

-- 각 유저 별로 아이템 평점 제곱의 합의 제곱근을 구한다. ||A||
DROP TABLE IF EXISTS prob_4_2;
CREATE  TABLE prob_4_2 AS
SELECT  a.user
      , SQRT(SUM(a.rating * a.rating)) AS sqrt_sum
  FROM  ratings a
 WHERE  a.rating > 0
 GROUP  BY a.user
 
-- 정규화 된 행렬과 전치행렬의 곱을 구한다. 
DROP TABLE IF EXISTS prob_4_3;
CREATE  TABLE prob_4_3 AS
SELECT  a.user AS user_i       -- 행렬 A의 사용자 (Row)
      , b.user AS user_j       -- 전치 행렬 B의 사용자 (Column)
      , SUM(a.sqrt_sum * b.sqrt_sum) AS dot_product
  FROM  prob_4_2 a
  JOIN  prob_4_2 b 
--     ON  a.user = b.user 
 GROUP  BY  a.user, b.user; 
 
-- 유사도 테이블 구하기
DROP TABLE IF EXISTS my_user_similarity;
CREATE  TABLE my_user_similarity AS
SELECT  a.user_i AS user_1
      , a.user_j AS user_2  
      , ROUND(a.dot_product / b.dot_product, 1) AS sim
  FROM  prob_4_1 a
  JOIN  prob_4_3 b
    ON  a.user_i = b.user_i
   AND  a.user_j = b.user_j

-- 자기 자신과의 유사도가 불필요하므로, 각 사용자의 자기 자신과의
-- 유사도는 최종 출력에 포함되지 않거나 0으로 대체
UPDATE  my_user_similarity
   SET  sim = 0
 WHERE  user_1 = user_2;
COMMIT;


-- 검증
SELECT  *
  FROM  my_user_similarity a
  JOIN  user_similarity b
    ON  a.user_1 = b.user_1
   AND  a.user_2 = b.user_2
 WHERE  a.sim != b.sim;

 
