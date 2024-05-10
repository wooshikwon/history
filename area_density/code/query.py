import pandas as pd

def xydata_query(mydate):
     query_template = f''' 
          select 'moaline' as brand
               , cast(call_idx as varchar) as ord_no
               , date_format(a.call_date + interval '9' hour, '%Y-%m-%d') as ord_date_ymd
               , is_b2b
               , cast(b.agency_idx as varchar) as ord_br_code
               , cast(b.shop_idx as varchar) as ord_st_code
               , b.shop_name as ord_st_name
               , cast(c.agency_idx as varchar) as cth_br_code
               , cast(a.rider_idx as varchar) as cth_wk_code
               , b.st_addr1
               , b.st_addr2
               , b.st_addr3
               , b.address_lng as sa_map_x
               , b.address_lat as sa_map_y
               , a.address_lng as ea_map_x
               , a.address_lat as ea_map_y
               , distance as km_product
               , a.call_date + interval '9' hour as ord_date
               , a.accept_date + interval '9' hour as cth_date
               , a.start_date + interval '9' hour as pickup_date
               , a.finish_date + interval '9' hour as finish_date
               , a.driver_income
               , a.delivery_price
               , a.sales_delivery_price
          from (
               select finish_date_ymd
                    , call_idx
                    , is_b2b
                    , shop_idx
                    , agency_idx
                    , rider_idx
                    , distance
                    , call_date
                    , accept_date
                    , start_date
                    , finish_date
                    , driver_income
                    , delivery_price
                    , sales_delivery_price
                    , address_lng
                    , address_lat
                from t1_partner_moaline.calls 
               where finish_date_ymd 
                     between date_format(date('{mydate}') - interval '6' day, '%Y-%m-%d')
                         and '{mydate}'
                 and state = '완료'
                 and call_type = '배달대행'
               ) a
          left join (
                    select shops.ymd
                         , shops.shop_idx
                         , shops.shop_name
                         , emd.si_do as st_addr1
                         , emd.si_gun_gu as st_addr2
                         , emd.eup_myeon_dong as st_addr3
                         , shops.agency_idx
                         , shops.address_lng
                         , shops.address_lat
                         from (
                              select ymd
                                   , shop_idx
                                   , shop_name
                                   , agency_idx
                                   , address_lng
                                   , address_lat
                              from t1_partner_moaline.shops_snapshot
                              where ymd
                                    between date_format(date('{mydate}') - interval '6' day, '%Y-%m-%d')
                                        and '{mydate}'
                              ) as shops
                    cross join (
                                   SELECT * 
                                   FROM t2_common.address
                                   ) as emd
                    where st_contains(st_geometryfromtext(emd.wkt), st_point(shops.address_lng, shops.address_lat))
                    ) b
                    on a.shop_idx = b.shop_idx
               and a.finish_date_ymd = b.ymd
          left join (
                    select ymd
                         , rider_idx
                         , agency_idx
                    from t1_partner_moaline.drivers_snapshot
                    where ymd
                          between date_format(date('{mydate}') - interval '6' day, '%Y-%m-%d')
                              and '{mydate}'
                    ) c
                 on a.rider_idx = c.rider_idx
                    and a.finish_date_ymd = c.ymd
      '''
     return query_template