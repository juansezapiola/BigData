********************************************************************************
*----------------            Data Base Assembling              ----------------* 
*----------------                                              ----------------*
*----------------	    Marotta, Salischiker, Zapiola          ----------------* 
*----------------				                               ----------------* 
*----------------          Universidad de San Andrés           ----------------* 
*----------------              Machine Learning                ----------------* 
*----------------				    2025                       ----------------* 
********************************************************************************


*clean 
clear all

*Directory 							
gl main "/Users/juansegundozapiola/Documents/Maestria/Big Data/BigData/RP"
gl input "$main/input"
gl output "$main/output"


*INDEX
*==============================================================================*
*0) Key ID for Households
*1) Identification of improved seeds adoption 
*2) HH Characteristics
*3) AGR Characteristics
*4) Final Merge: HH_CHAR + AGR_CHAR
*==============================================================================*


*0) Key ID for Households
*==============================================================================*

*Creamos una base con los ID de los hogares del 2019.

use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_h.dta", clear

*Vemos si hay hogares duplicados 
bysort case_id: gen dup_count = _n
keep if dup_count==1

keep case_id
save "$input/key_id_2019.dta", replace

*8798 HH


*1) Identification of improved seeds adoption
*==============================================================================*

*Open seeds database.

use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_h.dta", clear


codebook crop_code
label list ag_H_seed_roster__id

/* Improved seeds: 3, 4, 12, 13, 14, 15, 18, 19, 20, 21, 24

           1 MAIZE LOCAL
           2 CMAIZE OMPOSITE/OPV
3 MAIZE HYBRID
4 MAIZE HYBRID RECYCLED
           5 TOBACCO BURLEY
		   6 TOBACCO FLUE CURED
           7 TOBACCO NNDF
           8 TOBACCO SDF
           9 TOBACCO ORIENTAL
          10 OTHER TOBACCO (SPECIFY)
          11 GROUNDNUT CHALIMBANA
12 GROUNDNUT CG7
13 GROUNDNUT MANIPINTA
14 GROUNDNUT MAWANGA
15 GROUNDNUT JL24
          16 OTHER GROUNDNUT (SPECIFY)
          17 RICE LOCAL
18 RICE FAYA
19 RICE PUSSA
20 RICE TCG10
21 RICE IET4094 (SENGA)
          22 RICE WAMBONE
          23 RICE KILOMBERO
24 RICE ITA
          25 RICE MTUPATUPA
          26 OTHER RICE (SPECIFY)
          27 GROUND BEAN(NZAMA)
          28 SWEET POTATO
          29 IRISH [MALAWI] POTATO
          30 WHEAT
          31 FINGER MILLET(MAWERE)
          32 SORGHUM
          33 PEARL MILLET(MCHEWERE)
          34 BEANS
          35 SOYABEAN
          36 PIGEONPEA(NANDOLO)
          37 COTTON
          38 SUNFLOWER
          39 SUGAR CANE
          40 CABBAGE
          41 TANAPOSI
          42 NKHWANI
          43 THERERE/OKRA
          44 TOMATO
          45 ONION
          46 PEA
          47 PAPRIKA
          48 OTHER (SPECIFY)

Source: FIFTH INTEGRATED HOUSEHOLD SURVEY 2019/20, Agriculture and Fishery Enumerator Manual (ANNEX 3)

*/


*We need to assign a binary number for those households that used an improved seed variety.

gen improved = .
replace improved = 1 if inlist(crop_code, 3, 4, 12, 13, 14, 15, 18, 19, 20, 21, 24)
replace improved = 0 if improved==.

bysort case_id: gen n = _n

* Assign 1 if the HH adopted, 0 otherwise. 
bysort case_id (crop_code): egen hh_improved = max(improved)


*we keep with a unique HH 
keep if n==1
tab hh_improved

/*
hh_improved |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |      4,043       45.95       45.95
          1 |      4,755       54.05      100.00
------------+-----------------------------------
      Total |      8,798      100.00
	  
4,755 HHs adopted an improved seed (54.05% of HHs)
*/


keep case_id hh_improved

label variable hh_improved "Improved seed adoption (1: Adopted ; 0: No)"


save "$input/hh_improved.dta", replace



*2) HH Characteristics
*==============================================================================*


/*
Household Characteristics:

Module B:
B03 sex
B04 relationship to head -> HH head gender
B05 age -> HH head age

Module C:
C09 Highest education

Module E:
E19 main wage job -> salaried employed

*/


*Module B

use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/HH_MOD_B.dta", clear

egen HH_head_fem = max(hh_b03 == 2 & hh_b04 == 1), by(case_id)
egen HH_head_age = max(hh_b05a * (hh_b04 == 1)), by(case_id)
replace HH_head_age=. if HH_head_age<1
replace HH_head_fem=. if HH_head_age==.

keep case_id PID HH_head_fem HH_head_age hh_b04



*Module C

merge 1:1 case_id PID using "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/HH_MOD_C.dta"

egen HH_head_edu= max(hh_c09 * (hh_b04 == 1)), by(case_id) 
replace HH_head_edu=. if HH_head_edu==0

keep case_id PID hh_b04 HH_head_fem HH_head_age  HH_head_edu


*Module E

merge 1:1 case_id PID using "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/HH_MOD_E.dta"

egen HH_head_salaried_emp = max(hh_e06_4 * (hh_b04 == 1)), by(case_id) //hh_e06_4 es hh_e18
*2=no 1=yes
replace HH_head_salaried_emp=. if HH_head_salaried_emp==0
replace HH_head_salaried_emp=0 if HH_head_salaried_emp==2

keep case_id PID HH_head_fem HH_head_age HH_head_edu HH_head_salaried_emp

bysort case_id: gen n=_n
keep if n==1
drop n PID

*Merge with those HH that cultivate.
merge 1:1 case_id using "$input/key_id_2019.dta"
drop if _merge==1
drop _merge

save "$input/HH_CHAR.dta", replace


*3) AGR Characteristics
*==============================================================================*


/*

Agriculture Characteristics:

Module H:
H03 coupons/vouchers for seeds -> for improved
H04 credit for seed -> for improved
H41 left over seeds 
Module T:
T01 advice obtained -> agriculture category 
Module C:
C04 plot size

*/



*Create a tempfile for the module T, to merge it to module H. 
use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_t1.dta", clear

codebook ag_t0a
label list ag_t0a //301 - New Seed Varieties

egen advice = max(ag_t0a == 301 & ag_t01 == 1), by(case_id)

bysort case_id: gen n=_n
keep if n==1
keep case_id advice

tempfile temp_data
save `temp_data'

use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_c.dta", clear

replace ag_c04c= ag_c04a if ag_c04c==.
bysort case_id: gen id=_n
keep case_id id ag_c04c
egen total_plot_size= total(ag_c04c), by(case_id) 
keep if id==1
keep case_id total_plot_size

tempfile temp_data_2
save `temp_data_2'


use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_h.dta", clear
*id for each seed cultivated (like plot id)
bysort case_id: gen id=_n

gen improved = .    
replace improved = 1 if inlist(crop_code, 3, 4, 12, 13, 14, 15, 18, 19, 20, 21, 24)
replace improved = 0 if improved==.

gen coupon_imp = (improved==1 & ag_h03==1)
gen credit_imp = (improved==1 & ag_h04==1)
gen left_over_seeds = (ag_h41==1)

keep case_id id improved coupon_imp credit_imp left_over_seeds

egen total_coupon = total(coupon_imp), by(case_id) // 1: hh used coupon to purchase improved seed.  
egen total_plots = count(coupon_imp), by(case_id) 
gen prop_coupon = total_coupon / total_plots //I have the proportion of plots that used coupons to purchase improved seeds

egen total_credit = total(credit_imp), by(case_id)   
gen prop_credit = total_credit / total_plots //I have the proportion of plots that used credit to purchase improved seeds 

egen total_left_seeds = total(left_over_seeds), by(case_id)   
gen prop_left_seeds = total_left_seeds / total_plots //I have the proportion of plots that used left over seeds 


keep if id==1

keep case_id prop_coupon prop_credit prop_left_seeds

merge m:1 case_id using `temp_data'
drop if _merge==2
drop _merge
merge 1:1 case_id using `temp_data_2', force

drop _merge


save "$input/AGRO_CHAR.dta", replace





*4) Final Merge: HH_CHAR + AGR_CHAR
*==============================================================================*

use "$input/hh_improved.dta", clear

merge 1:1 case_id using "$input/HH_CHAR.dta", force
drop _merge

merge 1:1 case_id using "$input/AGRO_CHAR.dta", force
drop _merge


tab HH_head_edu, gen(education_)
drop HH_head_edu education_8 education_9


label variable HH_head_fem "Female head in household"
label variable HH_head_age "Age of household head"
label variable HH_head_salaried_emp "Proportion being salaried employed"
label variable education_1 "head with no education"
label variable education_2 "head with PSLC education"
label variable education_3 "head with JCE education"
label variable education_4 "head with MSCE education"
label variable education_5 "head with NON-UNIV.DIPLOMA education"
label variable education_6 "head with UNIVER.DIPLOMA DEGREE education"
label variable education_7 "head with POST-GRAD.DIPLOMA DEGREE education"
label variable total_plot_size "Plot size (ACRES)"
label variable prop_coupon "Proportion of plot that used coupons/vouchers for improved seeds"
label variable prop_credit "Proportion of plot who had credit for improved seeds"
label variable prop_left_seeds "Proportion of plot who used seed left over from a previous season"
label variable advice "Obtained agriculture advice"


save "$input/MWI_final.dta", replace


































