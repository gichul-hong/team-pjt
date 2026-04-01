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

DROP TABLE if EXISTS prob_2_1;
CREATE TABLE prob_2_1 AS
SELECT  user
      , CASE WHEN COUNT(rating) = 1 THEN 0 ELSE MIN(rating) END AS min_rating
      , MAX(rating) AS max_rating
      , COUNT(rating) AS cnt
  FROM  ratings
 WHERE  rating IS NOT NULL
 GROUP  BY user;
 
-- COMMIT;
DROP TABLE if EXISTS prob_2_2;
CREATE TABLE prob_2_2 AS
SELECT  a.user AS user
      , a.item AS item
      , ROUND((a.rating - b.min_rating) / (b.max_rating - b.min_rating), 4) AS adj_rating 
  FROM  ratings a
  JOIN  prob_2_1 b
    ON  a.user = b.user
 WHERE  a.rating IS NOT NULL;
 
COMMIT;


-- 보정된 점수를 기반으로 아이템 별 사용자가 부여한 평점의 평균 구하기
SELECT  item
      , ROUND(AVG(adj_rating), 4) AS avg_rating
  FROM  prob_2_2
 GROUP  BY item
 ;
 
        SELECT  a.item AS item
              , COUNT(a.rating) AS prediction
          FROM  prob_2_2 a
         WHERE  1 = 1
           AND  a.item NOT IN ( SELECT  item
                                  FROM  ratings
                                 WHERE  user = {user}
                                   AND  rating IS NOT NULL ) 
           AND  a.rating IS NOT NULL
         GROUP  BY a.item
         ORDER  BY prediction DESC, a.item ASC
         LIMIT  {rec_num}
