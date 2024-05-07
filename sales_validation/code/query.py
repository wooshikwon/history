#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd


# # query functions 제작

# In[3]:


def hq_profit_query(mydate):
    query_template = f"""
        with st_info as (
            select st.st_code
                , emd.si_do as area_depth1
                , emd.si_gun_gu as area_depth2
                , emd.eup_myeon_dong as area_depth3
            from (
                    select st_code
                        , st_map_x
                        , st_map_y
                    from (
                            select *
                                , row_number() over(partition by st_code order by load_date_ymd desc) as rank
                            from (
                                select st_code
                                    , st_map_x
                                    , st_map_y
                                    , load_date_ymd
                                    from t1_db_o2o_stts_appsis.ald_grp_st_info
                                where load_date_ymd 
                                        between concat(substr('{mydate}', 1,7), '-01')
                                            and '{mydate}'
                                    and st_map_x is not null
                                    and st_map_y is not null
                                group by 1,2,3,4
                                )
                            )
                    where rank = 1
                    ) as st
            cross join (
                        select * 
                        from t2_common.address
                        ) as emd
            where st_contains(st_geometryfromtext(emd.wkt), st_point(cast(st.st_map_x as double), cast(st.st_map_y as double)))
            )
            , base as (
            select substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1,7) as ym
                , *
            from st_info
            
            union

            select substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1,7) as ym
                , *
            from st_info
            )
            ,ord_df as (
            select substr(date_format(ord_date + interval '2' hour, '%Y-%m-%d'), 1,7) as ym
                , ord_no
                , ord_st_code
                , ord_status_cd
                , cth_hd_code
                , ord_hd_code
                , cth_br_code
                , ord_br_code
                , hq_bl_yn
                , sl_a0_a
                , sl_b0_a
                , sl_l0_a
                , dvry_adj_amt
                , dvry_prch_amt
                , bl_ca_a
                , bl_ca3_a
                , wl_c
                , wl_a
                , wl_t
                , ql_a0_a
                , ql_d0_a
                , ql_d9_a
                , bl_ha_a
                , bl_bhd_a
                , bl_cc_a
                , bl_cc3_a
                , bl_cbl_a
                , bl_oc3_a
                , bl_obd_a
                , bl_obl_a
                , bl_oba_a
                , ql_a3_v
                , ql_t
            from t1_db_o2o_stts_appsis.ald_a01_stt_2017
            where ord_date_ymd 
                    between concat(substr(date_format(date('{mydate}') - interval '2' month - interval '1' day, '%Y-%m-%d'), 1,7), '-01')
                        and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                and date_format(ord_date + interval '2' hour, '%Y-%m-%d')
                    between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1,7), '-01')
                        and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
            )
            ,b2b as (
            select ym
                , ord_st_code
                , count(distinct ord_no) "br_cnt_cnt_b2b"
                , sum(ql_a0_a) "hq_rev_advances_b2b"
                , sum(bl_oba_a) "hq_exp_subsidy_b2b"
                , sum(ql_d0_a) "hq_rev_brfee_b2b"
                , sum(ql_d9_a) "hq_rev_taxagencyfee_b2b"
            from ord_df
            where ord_hd_code = 'H0095' 
            group by 1,2
            )
            ,roadshop as (
            select ym
                , ord_st_code
                , count(distinct ord_no) "br_cnt_cnt_roadshop"
                , sum(ql_d0_a) "hq_rev_brfee_roadshop"
                , sum(ql_d9_a) "hq_rev_taxagencyfee_roadshop"
            from ord_df
            where ord_hd_code != 'H0095'
            group by 1,2
            ) 
            ,manage_br_cash as (
            select substr(date_format(in_date + interval '2' hour, '%Y-%m-%d'), 1,7) as ym
                , b.area_depth1
                , b.area_depth2
                , b.area_depth3
                , coalesce(sum(case when br_cash_type_cd = 'B5' then -add_amt 
                            else 0 
                            end), 0) as "hq_rev_affilmgmtfee_monthlyfee"
            from t1_db_o2o_stts_appsis.ald_adj_br_cash_log a
            left join (
                        select br.br_code
                            , emd.si_do as area_depth1
                            , emd.si_gun_gu as area_depth2
                            , emd.eup_myeon_dong as area_depth3
                        from (
                                select br_code
                                    , br_map_x
                                    , br_map_y
                                from (
                                    select *
                                            , row_number() over(partition by br_code order by load_date_ymd desc) as rank
                                        from (
                                            select br_code
                                                , br_map_x
                                                , br_map_y
                                                , load_date_ymd
                                                from t1_db_o2o_stts_appsis.ald_grp_br_info
                                            where load_date_ymd 
                                                    between concat(substr('{mydate}', 1,7), '-01')
                                                        and '{mydate}'
                                                and br_map_x is not null
                                                and br_map_y is not null
                                            group by 1,2,3,4
                                            )
                                    )
                                where rank = 1
                                ) as br
                        cross join (
                                    select * 
                                    from t2_common.address
                                    ) as emd
                        where st_contains(st_geometryfromtext(emd.wkt), st_point(cast(br.br_map_x as double), cast(br.br_map_y as double)))
                        ) b
                    on a.br_code = b.br_code
            where in_date_ymd 
                    between concat(substr(date_format(date('{mydate}') - interval '2' month - interval '1' day, '%Y-%m-%d'), 1,7), '-01')
                        and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                and date_format(in_date + interval '2' hour, '%Y-%m-%d')
                    between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1,7), '-01')
                        and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                and ord_no is null
                and br_cash_type_cd in ('B2', 'B5')
            group by 1,2,3,4
            )
            ,result as (
            select a.ym
                , a.st_code
                , a.area_depth1
                , a.area_depth2
                , a.area_depth3
                
                --- B2B
                , coalesce(b."br_cnt_cnt_b2b", 0) as "br_cnt_cnt_b2b"
                , coalesce(b."hq_rev_advances_b2b", 0) as "hq_rev_advances_b2b"
                , coalesce(b."hq_rev_brfee_b2b", 0) as "hq_rev_brfee_b2b"
                , coalesce(b."hq_rev_taxagencyfee_b2b", 0) as "hq_rev_taxagencyfee_b2b"
                , coalesce(b."hq_exp_subsidy_b2b", 0) as "hq_exp_subsidy_b2b"
                
                --- 로드샵
                , coalesce(c."br_cnt_cnt_roadshop", 0) as "br_cnt_cnt_roadshop"
                , coalesce(c."hq_rev_brfee_roadshop", 0) as "hq_rev_brfee_roadshop"
                , coalesce(c."hq_rev_taxagencyfee_roadshop", 0) as "hq_rev_taxagencyfee_roadshop"
            from base a
            left join roadshop c 
                    on a.st_code = c.ord_st_code 
                        and a.ym = c.ym
            left join b2b b
                    on a.st_code = b.ord_st_code
                        and a.ym = b.ym
            where ("br_cnt_cnt_b2b" > 0
                or "br_cnt_cnt_roadshop" > 0)
            )
                
            select a.ym
                , a.area_depth1
                , a.area_depth2
                , a.area_depth3
                , a.hq_overallmargin + coalesce(b.hq_rev_affilmgmtfee_monthlyfee, 0) as hq_overallmargin
                , a.hq_margin_roadshop
                , a.hq_taxagencyfee_roadshop
                , a.hq_margin_b2b
                , a.hq_taxagencyfee_b2b
                , a.br_cnt_roadshop
                , a.br_cnt_b2b
                , coalesce(b.hq_rev_affilmgmtfee_monthlyfee, 0) as hq_affilmgmtfee_monthlyfee
            from (
                    select a.ym
                        , a.area_depth1
                        , a.area_depth2
                        , a.area_depth3
                        , sum(hq_rev_advances_b2b
                            + hq_rev_brfee_b2b
                            + hq_exp_subsidy_b2b
                            + hq_rev_brfee_roadshop
                            + hq_rev_taxagencyfee_roadshop
                            + hq_rev_taxagencyfee_b2b
                            ) as hq_overallmargin
                                
                        , sum(hq_rev_brfee_roadshop
                            ) as hq_margin_roadshop
                            
                        , sum(hq_rev_taxagencyfee_roadshop
                            ) as hq_taxagencyfee_roadshop
                            
                        , sum(hq_rev_advances_b2b
                            + hq_rev_brfee_b2b
                            + hq_exp_subsidy_b2b
                            ) as hq_margin_b2b
                            
                        , sum(hq_rev_taxagencyfee_b2b
                            ) as hq_taxagencyfee_b2b
                            
                        , sum(br_cnt_cnt_roadshop
                            ) as br_cnt_roadshop
                        
                        , sum(br_cnt_cnt_b2b
                            ) as br_cnt_b2b
                    from result a
                group by 1,2,3,4
                    ) a
                left join manage_br_cash b
                    on a.area_depth1 = b.area_depth1
                        and a.area_depth2 = b.area_depth2
                        and a.area_depth3 = b.area_depth3
                        and a.ym = b.ym
        """
    return query_template


# In[4]:


def market_size_query(mydate):
    query_template = f"""
        with od_ratio as (
        select '강원특별자치도' AS address1, 0.006 AS bm_od_ratio, 0.028 AS ygy_od_ratio union all
        select '경기도', 0.165, 0.08 union all
        select '경상남도', 0.013, 0.028 union all  -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        select '경상북도', 0.011, 0.028 union all  -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        select '광주광역시', 0.053, 0.055 union all
        select '대구광역시', 0.039, 0.055 union all
        select '대전광역시', 0.053, 0.055 union all
        select '부산광역시', 0.045, 0.055 union all
        select '서울특별시', 0.438, 0.6 union all
        select '세종특별자치시', 0.05, 0.028 union all  -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        select '울산광역시', 0.022, 0.028 union all  -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        select '인천광역시', 0.153, 0.1 union all
        select '전라남도', 0.007, 0.028 union all  -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        select '전북특별자치도', 0.024, 0.028 union all  -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        select '제주특별자치도', 0.017, 0.028 union all  -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        select '충청남도', 0.022, 0.028 union all  -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        select '충청북도', 0.021, 0.028           -- ygy_od_ratio가 누락된 지역에 대한 기본값 0.028 사용
        )
        ,fixed_nonfnb_fnb_ratio as (
        select 0.925 as fix_fnb_ratio
            , 0.075 as fix_non_fnb_ratio
            , 0.1   as fix_call_ratio
        )
        ,ym_int as (
        select cast(replace(substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1,7), '-', '') as int) as thismonth
            , cast(replace(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1,7), '-', '') as int) as lastmonth
        )
        ,dvry_population_index as (
        select a.ym
            , a.area_depth1
            , a.area_depth2
            , b.age_seg
            , a.population * b.ratio as "dvry_population_index"
          from (
                select case when area_depth1 = '전북' then '전북특별자치도'
                            when area_depth1 = '강원도' then '강원특별자치도'
                            else area_depth1
                            end as area_depth1
                    , area_depth2
                    , age_seg
                    , value as "population"
                    , ym
                  from t1_thirdparty_ms.ms_population_by_age_m 
                where not(area_depth2 = '' and area_depth1 != '세종특별자치시')
                  and area_depth2 not in ('부천시', '고양시', '성남시', '수원시', '안산시', '안양시', '용인시', '전주시', '창원시', '천안시', '청주시', '포항시')
                  and (area_depth2 !='nan' or area_depth1 like '%세종%')
                  and ym 
                      between (select lastmonth from ym_int)  
                          and (select thismonth from ym_int)  
                ) a
          left join (
                    select distinct 
                          ym
                        , substring(tag_nm,9,3) as "age_seg"
                        , value as "ratio"
                      from t1_thirdparty_ms.ms_ref_m
                    where TAG_NM like '%배달인구구성비%'
                    order by 1 desc
                    limit 7
                    ) b
                on a.age_seg = b.age_seg
        )
        ,index_sum as (
        select ym
            , area_depth1
            , area_depth2
            , sum(dvry_population_index)*1.0 as "sigungu_index_sum"
          from dvry_population_index
        group by grouping sets ((ym, area_depth1, area_depth2), (ym))
        )
        ,sigungu_dvry_population_rate as (
        select a.ym
            , a.area_depth1
            , a.area_depth2
            , a.sigungu_index_sum / b.overall_index_sum *1.0 as "sigungu_dvry_population_rate"
          from index_sum a
          left join (
                    select ym 
                        , sigungu_index_sum as overall_index_sum
                      from index_sum
                    where area_depth1 is null
                      and area_depth2 is null
                    ) b
                  on a.ym = b.ym
        where a.area_depth1 is not null
        )
        ,sigungu_dvry_turnover as (
        select a.ym
            , a.area_depth1
            , a.area_depth2 
            , b.value * a.sigungu_dvry_population_rate as "dvry_turnover"
          from sigungu_dvry_population_rate a
          left join t1_thirdparty_ms.ms_ref_m b 
                on a.ym = b. ym
        where b.tag_nm = '음식서비스거래액'
          and b.ym 
              between (select lastmonth from ym_int)  
                  and (select thismonth from ym_int)  
        )
        ,platform_ratio as (
        select ym
            , case when area_depth1 = '강원' then '강원특별자치도'
                    when area_depth1 = '경기' then '경기도'
                    when area_depth1 = '경남' then '경상남도'
                    when area_depth1 = '경북' then '경상북도'
                    when area_depth1 = '광주' then '광주광역시'
                    when area_depth1 = '대구' then '대구광역시'
                    when area_depth1 = '대전' then '대전광역시'
                    when area_depth1 = '부산' then '부산광역시'
                    when area_depth1 = '서울' then '서울특별시'
                    when area_depth1 = '세종' then '세종특별자치시'
                    when area_depth1 = '울산' then '울산광역시'
                    when area_depth1 = '인천' then '인천광역시'
                    when area_depth1 = '전남' then '전라남도'
                    when area_depth1 = '전북' then '전북특별자치도'
                    when area_depth1 = '제주' then '제주특별자치도'
                    when area_depth1 = '충남' then '충청남도'
                    when area_depth1 = '충북' then '충청북도'
                    end as area_depth1
            , case when area_depth1 = '세종' then 'nan'
                    else area_depth2
                    end as area_depth2
            , coalesce(sum(case when service_nm = '배달의민족' then tot_amt end)*1.0 / (sum(tot_amt)*1.0), 0)  as "bm_ratio"
            , coalesce((sum(case when service_nm = '요기요' then tot_amt end)*1.0) / (sum(tot_amt)*1.0), 0)    as "ygy_ratio"
            , coalesce((sum(case when service_nm = '쿠팡이츠' then tot_amt end)*1.0) / (sum(tot_amt)*1.0), 0)  as "cp_ratio"
          from t1_thirdparty_ms.card_stats_m
          where not (ym = 202208 and card_company_nm = 'lotte')
            and ym 
                between (select lastmonth from ym_int)  
                    and (select thismonth from ym_int)  
        group by 1,2,3
        )
        ,direct_payment_ratio as ( -- 변경대상 -> ms_ref_m tag_nm='현장결제비중'
        select ym
            , value as "pay_ratio"
          from t1_thirdparty_ms.ms_ref_m
        where tag_nm like '%현장%'
          and ym 
              between (select lastmonth from ym_int)  
                  and (select thismonth from ym_int)  
          and value > 0
        )
        ,platform_transaction as (
        select ym
            , case when ym < 202208 then 24439.37 else (coalesce(sum(case when service_nm = '배달의민족' then tot_amt end)*1.0 / sum(case when service_nm = '배달의민족' then tot_cnt end),0))end as "bm_transaction" -- 202208 신한카드 데이터 평균단가
            , case when ym < 202208 then 19525.32 else (coalesce(sum(case when service_nm = '요기요' then tot_amt end)*1.0 / sum(case when service_nm = '요기요' then tot_cnt end),0)) end as "ygy_transaction" -- 202208 신한카드 데이터 평균단가
            , case when ym < 202208 then 26418.79 else (coalesce(sum(case when service_nm = '쿠팡이츠' then tot_amt end)*1.0 / sum(case when service_nm = '쿠팡이츠' then tot_cnt end),0)) end as "cp_transaction" -- 202208 신한카드 데이터 평균단가
          from t1_thirdparty_ms.card_stats_m
        where not (ym = 202208 and card_company_nm = 'lotte')
          and ym 
              between (select lastmonth from ym_int)  
                  and (select thismonth from ym_int)  
          group by 1
        )
        ,dvry_platform_cnt as (
        select a.ym
            , a.area_depth1
            , case when area_depth1 = '세종특별자치시' and area_depth2 = 'nan' then '세종특별자치시'
                   else area_depth2
                   end as area_depth2
            , case when d.bm_transaction = 0 then 0 
                        else coalesce(((a.dvry_turnover * b.bm_ratio)/(1-((1- od_ratio.bm_od_ratio)*c.pay_ratio)))/d.bm_transaction*1.0, 0) 
                          end as "bm_area_count" -- 기존 0.83
            , case when d.ygy_transaction = 0 then 0 
                        else coalesce(((a.dvry_turnover * b.ygy_ratio)/((0.125*c.pay_ratio)+1-c.pay_ratio))/d.ygy_transaction *1.0, 0) 
                          end  as "ygy_area_count"
            , case when d.cp_transaction = 0 then 0 
                        else coalesce((a.dvry_turnover * b.cp_ratio)/d.cp_transaction *1.0, 0) 
                            end as "cp_area_count"
          from sigungu_dvry_turnover a
          left join od_ratio
                on a.area_depth1 = od_ratio.address1
          left join platform_ratio b
                on a.ym = b.ym 
                    and a.area_depth1 = b.area_depth1 
                    and replace(a.area_depth2, ' ','') = replace(b.area_depth2, ' ','')
          left join direct_payment_ratio c 
                on a.ym = c.ym
          left join platform_transaction d 
                on a.ym = d.ym
          )
        ,nonfnb_fnb_ratio as (
        select cast(replace(a.ord_date,'-','') as bigint)/100 as ym
              , sum(case when c.cate1 not like '%Non%' and c.cate1 not like '%의료%' then a.d_fin else 0 end)*1.00 / sum(a.d_fin)*1.00 as fnb_ratio
              , sum(case when c.cate1 like '%Non%' or c.cate1 like '%의료%' then a.d_fin else 0 end)*1.00 / sum(a.d_fin)*1.00 as nonfnb_ratio
        from t2_service_o2o.st_ord_dvry_daily a
        left join (
                select *
                  from t1_db.t1_st_category
                where ymd = (select thismonth*100+1 from ym_int)
                ) c
              on a.ord_st_code = c.st_code
        where cast(replace(a.ord_date,'-','') as bigint)/100
              between (select lastmonth from ym_int)  
                  and (select thismonth from ym_int)  
        group by 1
        )

        select concat(substr(cast(a.ym as varchar), 1, 4), '-', substr(cast(a.ym as varchar), 5, 2)) as ym
            , area_depth1
            , area_depth2
            , cast(sum(
              (a.bm_area_count*(1-nonfnb_ratio) + a.ygy_area_count*(1-nonfnb_ratio) + a.cp_area_count 
            + ((a.bm_area_count*(1-nonfnb_ratio) + a.ygy_area_count*(1-nonfnb_ratio) + a.cp_area_count)/(1-(select fix_call_ratio from fixed_nonfnb_fnb_ratio))*(select fix_call_ratio from fixed_nonfnb_fnb_ratio)))
            + ((a.bm_area_count/(select fix_fnb_ratio from fixed_nonfnb_fnb_ratio)*(1-(select fix_fnb_ratio from fixed_nonfnb_fnb_ratio))) + (a.bm_area_count * nonfnb_ratio)   
            + (a.ygy_area_count/(select fix_fnb_ratio from fixed_nonfnb_fnb_ratio)*(1-(select fix_fnb_ratio from fixed_nonfnb_fnb_ratio))) + (a.ygy_area_count * nonfnb_ratio))
            ) as int) as "market_cnt"
            , cast(sum((a.bm_area_count 
                * b.bm_od_ratio) 
                + (a.ygy_area_count
                * ygy_od_ratio)
                + a.cp_area_count
                + (a.bm_area_count/(select fix_fnb_ratio from fixed_nonfnb_fnb_ratio)*(1-(select fix_fnb_ratio from fixed_nonfnb_fnb_ratio)))
                + (a.ygy_area_count/(select fix_fnb_ratio from fixed_nonfnb_fnb_ratio)*(1-(select fix_fnb_ratio from fixed_nonfnb_fnb_ratio)))) as int) as "ordinary_delivery_cnt"
        from dvry_platform_cnt a
        left join od_ratio b
              on a.area_depth1 = b.address1
        left join nonfnb_fnb_ratio c 
              on a.ym = c.ym
        group by 1,2,3
        order by 1 desc
      """
    return query_template


# In[5]:


def new_hurbs_query(mydate):
     query_template = f"""
          with t2_ord as ( 
          -- 지난 6개월간 허브들의 수행일과 발주일을 중복 제거해 결합
          select cth_br_code
               , cast(date_format(ord_date + interval '2' hour, '%Y%m%d') as int) ymd
          from t1_db_o2o_stts_appsis.ald_a01_record
          where ord_status_cd = 3
          and ord_date_ymd 
               between date_format(((date('{mydate}') - interval '6' month) - interval '1' day), '%Y-%m-%d') 
                    and date_format(date('{mydate}'), '%Y-%m-%d')
          and date_format(ord_date + interval '2' hour, '%Y-%m-%d')
               between date_format(date('{mydate}') - interval '6' month, '%Y-%m-%d') 
                    and date_format(date('{mydate}'), '%Y-%m-%d')
          group by 1,2

          union
          
          select ord_br_code as cth_br_code
               , cast(date_format(ord_date + interval '2' hour, '%Y%m%d') as int) ymd
          from t1_db_o2o_stts_appsis.ald_a01_record
          where ord_status_cd = 3
          and ord_date_ymd 
               between date_format(((date('{mydate}') - interval '6' month) - interval '1' day), '%Y-%m-%d') 
                    and date_format(date('{mydate}'), '%Y-%m-%d')
          and date_format(ord_date + interval '2' hour, '%Y-%m-%d')
               between date_format(date('{mydate}') - interval '6' month, '%Y-%m-%d') 
                    and date_format(date('{mydate}'), '%Y-%m-%d')
          and ord_hd_code != 'H0095'
          group by 1,2
          )
          ,lag5 as ( 
          -- 연속 수행/발주를 했다면 5일전이어야 할, 4번째 전 수행/발주일을 가져옴
          select *
               , lag(ymd,4) over(partition by cth_br_code order by ymd) as lag5_ymd
          from t2_ord
          )
          ,consistence as ( 
          -- 4번째 전 수행일과 현재 날짜의 차이를 구함. 연속수행/발주를 하고 있다면 그 값은 4여야만 함
          select *
               , date_diff('day', date_parse(cast(lag5_ymd as varchar), '%Y%m%d'), date_parse(cast(ymd as varchar), '%Y%m%d')) as from_lastday
          from lag5
          )
          ,consistence5_week as ( 
          -- 그 값이 4인 것은, 특정일이 5일 연속 수행이 이뤄지고 있는 날이라는 뜻임. 
          -- 5일 연속수행이 존재하는 주(week_index) 번호와 이번주까지 5일이상 연속수행이 시작된 최초일을 확인함(firstday) : 최소값은 목요일임
          select cth_br_code
               , date_format(date_parse(cast(min(lag5_ymd) as varchar), '%Y%m%d'), '%Y-%m-%d') as firstday
          from consistence
          where from_lastday = 4
          group by 1
          )
          ,new_hurb_list as ( 
          -- 지난달과 지지난달에 연속수행 주 판정을 받았는데, 그 전에는 한번도 연속수행 판정주가 없었으면 신규허브임
          select a.*
               , b.max_ymd
               , b.count_ymd
          from consistence5_week a
          left join (
                    select cth_br_code
                         , date_format(date_parse(cast(max(ymd) as varchar), '%Y%m%d'), '%Y-%m-%d') as max_ymd
                         , count(distinct ymd) as count_ymd
                    from t2_ord
                    group by 1
                    ) b
                    on a.cth_br_code = b.cth_br_code
          where a.cth_br_code not in ('B1430', 'B3373', 'B1811', 'B6738')
          and a.firstday 
               between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')
               and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
          ),
          newhurb_stlist as ( -- 신규허브의 '첫 연속 5일수행의 첫날'(first_day)
                              -- 신규허브가 이번달에 가지고 있는 상점 리스트를 확인함
          select a.*
               , b.st_code
          from new_hurb_list a
          join (
               select st_code
                    , br_code
               from (
                    select st_code
                         , br_code
                         , row_number() over(partition by st_code, br_code order by load_date_ymd desc) as rank
                         from t1_db_o2o_stts_appsis.ald_grp_st_info 
                         where load_date_ymd
                              between concat(substr('{mydate}', 1,7), '-01')
                                   and '{mydate}'
                         and use_yn = 'Y'
                    )
               where rank = 1
               group by 1,2
               ) b 
               on a.cth_br_code = b.br_code
          ),
          newhurbst_lastmonth as ( -- 신규허브가 이번주에 가지고 있는 상점이 지지난달 1일에는 어떤 허브 소속이었는지 확인함
          select a.st_code
               , b.br_code
          from newhurb_stlist a
          join (
               select st_code, br_code
               from (
                    select st_code
                         , br_code
                         , row_number() over(partition by st_code, br_code order by load_date_ymd desc) as rank
                    from t1_db_o2o_stts_appsis.ald_grp_st_info 
                    where load_date_ymd
                         between concat(substr(date_format(date('{mydate}') - interval '3' month, '%Y-%m-%d'),1,7),'-01')
                              and date_format(date(concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                    )
               where rank = 1
               group by 1,2
               ) b
          on a.st_code = b.st_code
          ),
          comparison as ( -- 신규허브 & 신규허브가 이번주에 보유한 상점 리스트 & 그 상점들이 4주전에 소속되었던 허브 가 나열된 테이블을 만듬
          select a.st_code
               , b.br_code
               , a.cth_br_code
          from newhurb_stlist a
          left join newhurbst_lastmonth b 
               on a.st_code = b.st_code
          )
          ,comparison2 as ( -- 상점을 기준으로 이번주 소속 허브와 4주전 소속허브가 다른 리스트를 만듬 (상점의 소속 변경으로 파악)
          select *
               , case when br_code != cth_br_code then 1
                    else 0
                    end as transfer
          from comparison
          )

          select substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1,7) as ym
               , c.cth_br_code as br_code
               , c.firstday
               , c.max_ymd
               , c.count_ymd
               , c.st_code
               , b.address1 as area_depth1
               , b.address2 as area_depth2
               , sum(a.ql_d0_a + a.ql_d9_a + a.ql_a0_a) as newhurbs_hq_profit
               , sum(case when ord_status_cd = 3 then 1 else 0 end) as newhurbs_cnt
          from (
               select ord_st_code
                    , ord_no
                    , ord_status_cd
                    , ql_d0_a
                    , ql_d9_a
                    , ql_a0_a
                    from t1_db_o2o_stts_appsis.ald_a01_stt_2017
               where ord_date_ymd 
                         between concat(substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1,7), '-01')
                              and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                    and ord_st_code in (
                                   select distinct st_code
                                        from comparison2
                                   where transfer = 0
                                   )
               ) a
          left join (
                    select st.st_code
                         , emd.si_do as address1
                         , emd.si_gun_gu as address2
                    from (
                         select *
                              , row_number() over(partition by st_code) as rank
                         from (
                                   select st_code
                                        , st_map_x
                                        , st_map_y
                                   from t1_db_o2o_stts_appsis.ald_grp_st_info
                                   where load_date_ymd 
                                        between concat(substr('{mydate}', 1,7), '-01')
                                             and '{mydate}'
                                   group by 1,2,3
                              )
                         ) as st
                    cross join (
                              SELECT * 
                              FROM t2_common.address
                              ) as emd
                    where st_contains(st_geometryfromtext(emd.wkt), st_point(cast(st.st_map_x as double), cast(st.st_map_y as double)))
                    and rank = 1
                    ) b
               on a.ord_st_code = b.st_code
          left join (
                    select cth_br_code
                         , st_code
                         , firstday
                         , max_ymd
                         , count_ymd
                    from newhurb_stlist
                         ) c
                    on a.ord_st_code = c.st_code
          group by 1,2,3,4,5,6,7,8
          """
     return query_template


# In[6]:


def churned_hurbs_query(mydate):
     query_template = f"""
          with t2_ord as ( 
          -- 지난 6개월간 허브들의 수행일과 발주일을 중복 제거해 결합
          select cth_br_code
               , cast(date_format(ord_date + interval '2' hour, '%Y%m%d') as int) ymd
          from t1_db_o2o_stts_appsis.ald_a01_record
          where ord_status_cd = 3
          and ord_date_ymd 
               between date_format(((date('{mydate}') - interval '6' month) - interval '1' day), '%Y-%m-%d') 
                    and date_format(date('{mydate}'), '%Y-%m-%d')
          and date_format(ord_date + interval '2' hour, '%Y-%m-%d')
               between date_format(date('{mydate}') - interval '6' month, '%Y-%m-%d') 
                    and date_format(date('{mydate}'), '%Y-%m-%d')
          group by 1,2

          union
          
          select ord_br_code as cth_br_code
               , cast(date_format(ord_date + interval '2' hour, '%Y%m%d') as int) ymd
          from t1_db_o2o_stts_appsis.ald_a01_record
          where ord_status_cd = 3
          and ord_date_ymd 
               between date_format(((date('{mydate}') - interval '6' month) - interval '1' day), '%Y-%m-%d') 
                    and date_format(date('{mydate}'), '%Y-%m-%d')
          and date_format(ord_date + interval '2' hour, '%Y-%m-%d')
               between date_format(date('{mydate}') - interval '6' month, '%Y-%m-%d') 
                    and date_format(date('{mydate}'), '%Y-%m-%d')
          and ord_hd_code != 'H0095'
          group by 1,2
          )
          ,lag5 as ( 
          -- 연속 수행/발주를 했다면 5일전이어야 할, 4번째 전 수행/발주일을 가져옴
          select *
               , lag(ymd,4) over(partition by cth_br_code order by ymd) as lag5_ymd
          from t2_ord
          )
          ,consistence as ( 
          -- 4번째 전 수행일과 현재 날짜의 차이를 구함. 연속수행/발주를 하고 있다면 그 값은 4여야만 함
          select *
               , date_diff('day', date_parse(cast(lag5_ymd as varchar), '%Y%m%d'), date_parse(cast(ymd as varchar), '%Y%m%d')) as from_lastday
          from lag5
          )
          ,consistence5_week as ( 
          -- 그 값이 4인 것은, 특정일이 5일 연속 수행이 이뤄지고 있는 날이라는 뜻임. 
          -- 5일 연속수행이 존재하는 주(week_index) 번호와 이번주까지 5일이상 연속수행이 시작된 최초일을 확인함(firstday) : 최소값은 목요일임
          select cth_br_code
          from consistence
          where from_lastday = 4
          group by 1
          )
          ,leavehurb_list as ( -- 최소 1번 이상 연속 5일을 수행해본 허브들의 가장 마지막 수행일/수행주차는 언제일까
          select cth_br_code
               , date_diff('day', date(max_ymd), date('{mydate}')) as nonactvie_day
               , frequency
               , max_ymd
               , date_add('day', cast(round((frequency+2)*3, 0) as int), date(max_ymd)) as decision_date
          from (
               select *
                    , (date_diff('day', date(min_ymd), date(max_ymd)) + 1)*1.00
                         / count_ymd*1.00 frequency
                    from (
                         select a.cth_br_code
                              , date_format(date_parse(cast(min(b.ymd) as varchar), '%Y%m%d'), '%Y-%m-%d') as min_ymd
                              , date_format(date_parse(cast(max(b.ymd) as varchar), '%Y%m%d'), '%Y-%m-%d') as max_ymd
                              , count(distinct b.ymd) as count_ymd
                         from consistence5_week a
                         left join t2_ord b 
                                   on a.cth_br_code = b.cth_br_code
                         group by 1
                         )
               )
          where (frequency+2)*3.00 < date_diff('day', date(max_ymd), date('{mydate}'))*1.00
          and max_ymd
               between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')
                    and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
          )
          ,leavehurb_stlist as ( -- '최신 이탈 허브'들이 전달에는 어떤 상점들을 보유하고 있었을까?
          select a.*
               , b.st_code
          from leavehurb_list a
          join (
               select st_code, br_code
               from (
                    select st_code
                         , br_code
                         , row_number() over(partition by st_code, br_code order by load_date_ymd desc) as rank
                         from t1_db_o2o_stts_appsis.ald_grp_st_info 
                         where load_date_ymd
                              between concat(substr(date_format(date('{mydate}') - interval '3' month, '%Y-%m-%d'),1,7),'-01')
                                   and date_format(date(concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                         and use_yn = 'Y'
                    )
               where rank = 1
               group by 1,2
               ) as b 
          on a.cth_br_code = b.br_code
          ),
          leavehurbst_thisweek as ( -- 최신 이탈허브가 이탈 전달에 가지고 있던 상점이 이번달에는 어떤 허브의 소속일까?
          select a.st_code
               , b.br_code
          from leavehurb_stlist a
          join (
               select st_code
                    , br_code
                    from (
                         select st_code
                              , br_code
                              , row_number() over(partition by st_code, br_code order by load_date_ymd desc) as rank
                         from t1_db_o2o_stts_appsis.ald_grp_st_info 
                         where load_date_ymd
                              between concat(substr('{mydate}', 1,7), '-01')
                                   and '{mydate}'
                         and use_yn = 'Y'
                    )
               where rank = 1
               group by 1,2
               ) as b 
          on a.st_code = b.st_code
          ),
          comparison as ( -- 최신 이탈허브가 이탈 전달에 보유하던 상점과 이번달에 상점의 소속 허브를 비교함
                         -- 이탈 전에는 보유했는데, 이탈 후에는 다른 허브가 보유하고 있는 않은 상점을 '타허브 이관 상점'으로 판별하겠음.
          select a.st_code
               , b.br_code -- 이번달 소속 허브
               , a.cth_br_code -- 이탈 허브
          from leavehurb_stlist a
          left join leavehurbst_thisweek b 
                    on a.st_code = b.st_code
          )
          ,comparison2 as ( -- 타허브 이관 상점 리스트
          select *
               , case when br_code != cth_br_code then 1
                    else 0
                    end as transfer
          from comparison
          )

          select substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1,7) as ym
               , c.*
               , b.si_do as area_depth1
               , b.si_gun_gu as area_depth2
               , b.eup_myeon_dong as area_depth3
               , sum(a.ql_d0_a + a.ql_d9_a + a.ql_a0_a) as churnedhurbs_hq_profit
               , sum(case when ord_status_cd = 3 then 1 else 0 end) as churnedhurbs_cnt
          from (
               select ord_st_code
                    , ord_no
                    , ord_status_cd
                    , ql_d0_a
                    , ql_d9_a
                    , ql_a0_a
                    from t1_db_o2o_stts_appsis.ald_a01_stt_2017
               where ord_date_ymd 
                         between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1,7), '-01')
                         and date_format(date(concat(substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                    and ord_st_code in (
                                   select distinct st_code -- 소속 미변경 상점
                                        from comparison2
                                   where transfer = 0
                                   )
               ) a
          left join (
                    select st.st_code
                         , emd.si_do
                         , emd.si_gun_gu
                         , emd.eup_myeon_dong
                         from (
                              select *
                                   , row_number() over(partition by st_code) as rank
                              from (
                                   select st_code
                                        , st_map_x
                                        , st_map_y
                                   from (
                                        select st_code
                                             , st_map_x
                                             , st_map_y
                                             , row_number() over(partition by st_code, st_map_x, st_map_y order by load_date_ymd desc) as rank
                                             from t1_db_o2o_stts_appsis.ald_grp_st_info
                                             where load_date_ymd 
                                                  between concat(substr(date_format(date('{mydate}') - interval '3' month, '%Y-%m-%d'), 1,7), '-01')
                                                       and date_format(date(concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                                        )
                              where rank = 1
                              group by 1,2,3
                              )
                              ) as st
                    cross join (
                                   SELECT * 
                                   FROM t2_common.address
                                   ) as emd
                    where st_contains(st_geometryfromtext(emd.wkt), st_point(cast(st.st_map_x as double), cast(st.st_map_y as double)))
                         and rank = 1
                    ) b
                    on a.ord_st_code = b.st_code
          left join (
                    select *
                         from leavehurb_stlist
                    ) c
                    on a.ord_st_code = c.st_code
          group by 1,2,3,4,5,6,7,8,9,10
          """
     return query_template


# In[7]:


def new_b2bstores_query(mydate):
    query_template = f"""
        with new_b2bstores as (
        select *
        from (
                select ord_st_code as st_code
                    , partner_code
                    , min(ord_date_ymd) as min_ymd
                    , max(ord_date_ymd) as max_ymd
                    , count(distinct ord_date_ymd) as count_ymd
                from t1_db_o2o_stts_appsis.ald_a01_record
                where ord_date_ymd 
                    between date_format(date('{mydate}') - interval '6' month, '%Y-%m-%d') 
                        and date_format(date('{mydate}'), '%Y-%m-%d')
                and ord_hd_code = 'H0095'
                group by 1,2
                )
        where count_ymd >= 5
        and min_ymd 
            between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')
                and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
        )

        select substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1,7) as ym
            , b.*
            , c.si_do as area_depth1
            , c.si_gun_gu as area_depth2
            , c.eup_myeon_dong as area_depth3
            , sum(a.ql_d0_a + a.ql_d9_a + a.ql_a0_a) as newb2bstores_hq_profit
            , sum(case when ord_status_cd = 3 then 1 else 0 end) as newb2bstores_cnt
        from t1_db_o2o_stts_appsis.ald_a01_stt_2017 a
        join (
                select *
                from new_b2bstores
                ) b
            on a.ord_st_code = b.st_code
        left join (
                    select st.st_code
                        , emd.si_do
                        , emd.si_gun_gu
                        , emd.eup_myeon_dong
                    from (
                            select *
                                , row_number() over(partition by st_code) as rank
                            from (
                                select st_code
                                        , st_map_x
                                        , st_map_y
                                    from (
                                        select st_code
                                            , st_map_x
                                            , st_map_y
                                            , row_number() over(partition by st_code, st_map_x, st_map_y order by load_date_ymd desc) as rank
                                            from t1_db_o2o_stts_appsis.ald_grp_st_info
                                        where load_date_ymd 
                                                between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1,7), '-01')
                                                    and '{mydate}'
                                            and st_name is not null
                                            and st_map_x is not null
                                            and st_map_y is not null
                                        )
                            where rank = 1
                            group by 1,2,3
                                )
                            ) as st
                    cross join (
                                SELECT * 
                                FROM t2_common.address
                                ) as emd
                    where st_contains(st_geometryfromtext(emd.wkt), st_point(cast(st.st_map_x as double), cast(st.st_map_y as double)))
                        and rank = 1
                    ) c
                on a.ord_st_code = c.st_code
        where a.ord_date_ymd 
                between concat(substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1, 7), '-01')
                    and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
        group by 1,2,3,4,5,6,7,8,9
        """
    return query_template


# In[8]:


def churned_b2bstores_query(mydate):
    query_template = f"""
        with churned_b2bstores as (
        select a.st_code
            , a.partner_code
            , date_diff('day', date(max_ymd), date('{mydate}')) as nonactvie_day
            , frequency
            , max_ymd
            , date_add('day', cast(round((frequency+2)*3, 0) as int), date(max_ymd)) as decision_date
        from (
                select *
                    , (date_diff('day', date(min_ymd), date(max_ymd)) + 1)*1.00
                    / count_ymd*1.00 frequency
                from (
                        select ord_st_code as st_code
                            , partner_code
                            , min(ord_date_ymd) as min_ymd
                            , max(ord_date_ymd) as max_ymd
                            , count(distinct ord_date_ymd) as count_ymd
                        from t1_db_o2o_stts_appsis.ald_a01_record
                        where ord_date_ymd 
                            between date_format(date('{mydate}') - interval '6' month, '%Y-%m-%d') 
                                and date_format(date('{mydate}'), '%Y-%m-%d')
                        and ord_hd_code = 'H0095'
                        and ord_status_cd = 3
                        group by 1,2
                        )
                where count_ymd >= 5
                ) a
        left join (
                    select st_code
                        , use_yn
                    from t1_db_o2o_stts_appsis.ald_grp_st_info
                    where load_date_ymd = '{mydate}'
                    ) b
                on a.st_code = b.st_code
        where (frequency+2)*3.00 < date_diff('day', date(max_ymd), date('{mydate}'))*1.00
            and max_ymd
                between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')
                    and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
            or use_yn = 'N'
        )

        select substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1,7) as ym
            , b.*
            , c.si_do as area_depth1
            , c.si_gun_gu as area_depth2
            , c.eup_myeon_dong as area_depth3
            , sum(a.ql_d0_a + a.ql_d9_a + a.ql_a0_a) as churnedb2bstores_hq_profit
            , sum(case when ord_status_cd = 3 then 1 else 0 end) as churnedb2bstores_cnt
        from t1_db_o2o_stts_appsis.ald_a01_stt_2017 a
        join (
                select *
                from churned_b2bstores
                ) b
            on a.ord_st_code = b.st_code
        left join (
                    select st.st_code
                        , emd.si_do
                        , emd.si_gun_gu
                        , emd.eup_myeon_dong
                    from (
                            select *
                                , row_number() over(partition by st_code) as rank
                            from (
                                select st_code
                                        , st_map_x
                                        , st_map_y
                                    from (
                                        select st_code
                                            , st_map_x
                                            , st_map_y
                                            , row_number() over(partition by st_code, st_map_x, st_map_y order by load_date_ymd desc) as rank
                                            from t1_db_o2o_stts_appsis.ald_grp_st_info
                                        where load_date_ymd 
                                                between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')
                                            and date_format(date(concat(substr('{mydate}', 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
                                        )
                            where rank = 1
                            group by 1,2,3
                                )
                            ) as st
                    cross join (
                                SELECT * 
                                FROM t2_common.address
                                ) as emd
                    where st_contains(st_geometryfromtext(emd.wkt), st_point(cast(st.st_map_x as double), cast(st.st_map_y as double)))
                        and rank = 1
                    ) c
                on a.ord_st_code = c.st_code
        where a.ord_date_ymd 
                between concat(substr(date_format(date('{mydate}') - interval '2' month, '%Y-%m-%d'), 1, 7), '-01')
                    and date_format(date(concat(substr(date_format(date('{mydate}') - interval '1' month, '%Y-%m-%d'), 1, 7), '-01')) - interval '1' day, '%Y-%m-%d')
        group by 1,2,3,4,5,6,7,8,9,10
        """
    return query_template

