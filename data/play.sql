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
 GROUP  BY a.user
 ORDER  BY 1 
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




-- #2
