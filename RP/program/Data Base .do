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
*4) COMM Characteristics
*5) Final Merge: HH_CHAR + AGR_CHAR
*==============================================================================*


*0) Key ID for Households
*==============================================================================*

*Creamos una base con los ID de los hogares del 2019.

use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_h.dta", clear

*Vemos si hay hogares duplicados 
bysort case_id: gen dup_count = _n
keep if dup_count==1

keep case_id

merge 1:1 case_id using "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/hh_mod_a_filt.dta", force
drop if _merge==2
keep case_id ea_id 

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
H37 seeds for free

Module T:
T01 advice obtained -> agriculture category 

Module C:
C04 plot size

Module D:
D58 -> Cover crops


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



use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_d.dta", clear
bysort case_id: gen id=_n
keep case_id id ag_d58 ag_d21 ag_d22 ag_d26 ag_d28a ag_d23 ag_d24a ag_d25a ag_d27

gen cover_crop = (ag_d58 == 1)  // Create a binary variable for cover crops
bysort case_id (id): gen total_plots = _N  // Count total plots per household
bysort case_id: gen cover_plots = sum(cover_crop)  // Count plots using cover crops per household
gen proportion_cover = cover_plots / total_plots  // Calculate proportion


label list ag_d21
/*
 1 Sandy (Mchenga)
 2 Between sandy &amp; clay(Pakati pa mchenga ndi katondo)
 3 Clay (Katondo)
 4 Other (Specify)
*/
gen sandy = (ag_d21 == 1) 
gen between = (ag_d21 == 2) 
gen clay = (ag_d21 == 3) 
gen other = (ag_d21 == 4) 
egen sandy_plots = total(sandy), by(case_id)
egen between_plots = total(between), by(case_id)
egen clay_plots = total(clay), by(case_id)
egen other_plots = total(other), by(case_id)

gen prop_sandy = sandy_plots / total_plots 
gen prop_between = between_plots / total_plots 
gen prop_clay = clay_plots / total_plots 
gen prop_other = other_plots / total_plots 



label list ag_d22

gen good = (ag_d22 == 1)
gen fair = (ag_d22 == 2)
gen poor = (ag_d22 == 3)

// Count the number of plots with each condition per household
foreach condition in good fair poor {
    egen `condition'_plots = total(`condition'), by(case_id)
}

// Calculate proportions
foreach condition in good fair poor {
    gen prop_`condition' = `condition'_plots / total_plots
}

label list ag_d26
/*
1 Flat
2 Slight slope
3 Moderate slope
4 Steep, hilly
*/

gen flat = (ag_d26 == 1)
gen slight = (ag_d26 == 2)
gen moderate = (ag_d26 == 3)		   
gen steep = (ag_d26 == 4)	

foreach condition in flat slight moderate steep {
    egen `condition'_plots = total(`condition'), by(case_id)
}

foreach condition in flat slight moderate steep {
    gen prop_`condition' = `condition'_plots / total_plots
}


label list irrigation
/*
1 Divert stream
2 Bucket
3 Hand pump
4 Treadle pump
5 Motor pump
6 Gravity
7 Rainfed/No irrigation
8 Other (Specify)
9 Can Irrigation
*/
gen divert_stream = (ag_d28a == 1)
gen bucket = (ag_d28a == 2)
gen hand_pump = (ag_d28a == 3)
gen treadle_pump = (ag_d28a == 4)
gen motor_pump = (ag_d28a == 5)
gen gravity = (ag_d28a == 6)
gen rainfed = (ag_d28a == 7)
gen other_ = (ag_d28a == 8)
gen can_irrigation = (ag_d28a == 9)

foreach method in divert_stream bucket hand_pump treadle_pump motor_pump gravity rainfed other_ can_irrigation {
    egen `method'_plots = total(`method'), by(case_id)
}

foreach method in divert_stream bucket hand_pump treadle_pump motor_pump gravity rainfed other_ can_irrigation {
    gen prop_`method' = `method'_plots / total_plots
}


label list ag_d23
/*
1 No Erosion
2 Low
3 Moderate
4 High
*/
gen no_erosion = (ag_d24 == 1)
gen low_erosion = (ag_d24 == 2)
gen moderate_erosion = (ag_d24 == 3)
gen high_erosion = (ag_d24 == 4)

foreach erosion in no_erosion low_erosion moderate_erosion high_erosion {
    egen `erosion'_plots = total(`erosion'), by(case_id)
}

foreach erosion in no_erosion low_erosion moderate_erosion high_erosion {
    gen prop_`erosion' = `erosion'_plots / total_plots
}

label list erosion
/*
1 Terrain
2 Flooding
3 Wind
4 Animals
5 Other (Specify)
*/
gen terrain = (ag_d24a == 1)
gen flooding = (ag_d24a == 2)
gen wind = (ag_d24a == 3)
gen animals = (ag_d24a == 4)
gen other_constraint = (ag_d24a == 5)

foreach constraint in terrain flooding wind animals other_constraint {
    egen `constraint'_plots = total(`constraint'), by(case_id)
}

foreach constraint in terrain flooding wind animals other_constraint {
    gen prop_`constraint' = `constraint'_plots / total_plots
}


label list control
/*
           1 No erosion control
           2 Terraces
           3 Erosion control bunds
           4 Gabions / Sandbags
           5 Vetiver grass
           6 Tree belts
           7 Water harvest bunds
           8 Drainage ditches
           9 Other (Specify)

*/

gen no_erosion_control = (ag_d25a == 1)
gen terraces = (ag_d25a == 2)
gen erosion_bunds = (ag_d25a == 3)
gen gabions_sandbags = (ag_d25a == 4)
gen vetiver_grass = (ag_d25a == 5)
gen tree_belts = (ag_d25a == 6)
gen water_harvest_bunds = (ag_d25a == 7)
gen drainage_ditches = (ag_d25a == 8)
gen other_erosion_control = (ag_d25a == 9)

foreach control in no_erosion_control terraces erosion_bunds gabions_sandbags vetiver_grass tree_belts water_harvest_bunds drainage_ditches other_erosion_control {
    egen `control'_plots = total(`control'), by(case_id)
}

foreach control in no_erosion_control terraces erosion_bunds gabions_sandbags vetiver_grass tree_belts water_harvest_bunds drainage_ditches other_erosion_control {
    gen prop_`control' = `control'_plots / total_plots
}



gen swamp = (ag_d27 == 1)  
bysort case_id: gen swamp_plots = sum(swamp) 
gen prop_swamp = swamp_plots / total_plots  

keep if id==1



keep case_id proportion_cover prop_sandy prop_between prop_clay prop_other prop_good prop_fair prop_poor prop_flat ///
prop_slight prop_moderate prop_steep prop_divert_stream prop_bucket prop_hand_pump prop_treadle_pump prop_motor_pump ///
prop_gravity prop_rainfed prop_other_ prop_can_irrigation prop_no_erosion prop_low_erosion prop_moderate_erosion ///
prop_high_erosion prop_terrain prop_flooding prop_wind prop_animals prop_other_constraint prop_no_erosion_control ///
prop_terraces prop_erosion_bunds prop_gabions_sandbags prop_vetiver_grass prop_tree_belts prop_water_harvest_bunds ///
prop_drainage_ditches prop_other_erosion_control prop_swamp

tempfile temp_data_3
save `temp_data_3'



use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_h.dta", clear
*id for each seed cultivated (like plot id)
bysort case_id: gen id=_n

gen improved = .    
replace improved = 1 if inlist(crop_code, 3, 4, 12, 13, 14, 15, 18, 19, 20, 21, 24)
replace improved = 0 if improved==.

gen coupon_imp = (improved==1 & ag_h03==1)
gen credit_imp = (improved==1 & ag_h04==1)
gen left_over_seeds = (ag_h41==1)
gen free_seed = (improved==1 & ag_h37==1)

keep case_id id improved coupon_imp credit_imp left_over_seeds free_seed

egen total_coupon = total(coupon_imp), by(case_id) // 1: hh used coupon to purchase improved seed.  
egen total_plots = count(coupon_imp), by(case_id) 
gen prop_coupon = total_coupon / total_plots //I have the proportion of plots that used coupons to purchase improved seeds

egen total_credit = total(credit_imp), by(case_id)   
gen prop_credit = total_credit / total_plots //I have the proportion of plots that used credit to purchase improved seeds 

egen total_left_seeds = total(left_over_seeds), by(case_id)   
gen prop_left_seeds = total_left_seeds / total_plots //I have the proportion of plots that used left over seeds 

egen total_free = total(free_seed), by(case_id)   
gen prop_free = total_free / total_plots 

keep if id==1

keep case_id prop_coupon prop_credit prop_left_seeds prop_free

merge m:1 case_id using `temp_data'
drop if _merge==2
drop _merge
merge 1:1 case_id using `temp_data_2', force
drop _merge
merge 1:1 case_id using `temp_data_3', force
drop _merge

save "$input/AGRO_CHAR.dta", replace


*4) COMM Characteristics
*==============================================================================*
use "$input/key_id_2019.dta", clear

/*
Community Characteristics:

Module F:
F07 assist agr ext der officer live?
F12 sellers of hybrid maize
F28 agriculture based project -> F30 main focus (1 & 9)

Module J:
J01 org that exist in community 
*/

use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/com_cf1.dta", clear

gen assistant_ag_officer = .
replace assistant_ag_officer=1 if com_cf07==1
replace assistant_ag_officer=0 if com_cf07==2

rename com_cf12 maize_hybrid_sellers

keep ea_id assistant_ag_officer maize_hybrid_sellers
bysort ea_id: gen n=_n

tempfile temp_data
save `temp_data'

use  "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/com_cf2.dta", clear
bysort ea_id: gen n=_n

gen agr_proj_yields =.
replace agr_proj_yields = 1 if com_cf30==1
replace agr_proj_yields = 0 if agr_proj_yields==.
egen total_yield_projects = total(agr_proj_yields), by(ea_id)

gen agr_proj_imp =.
replace agr_proj_imp = 1 if com_cf30==9
replace agr_proj_imp = 0 if agr_proj_imp==.
egen total_imp_projects = total(agr_proj_imp), by(ea_id)

keep if n==1

keep ea_id total_yield_projects total_imp_projects


merge 1:1 ea_id using `temp_data', force
drop _merge
replace total_yield_projects=0 if total_yield_projects==.
replace total_imp_projects=0 if total_imp_projects==.
drop n

merge 1:m ea_id using "$input/key_id_2019.dta", force
drop if _merge==1
drop _merge
save "$input/COMM_CHAR.dta", replace





*5) Final Merge: HH_CHAR + AGR_CHAR
*==============================================================================*

use "$input/hh_improved.dta", clear

merge 1:1 case_id using "$input/HH_CHAR.dta", force
drop _merge

merge 1:1 case_id using "$input/AGRO_CHAR.dta", force
drop _merge

merge 1:1 case_id using "$input/COMM_CHAR.dta", force
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
label variable prop_coupon "Proportion of improved seeds bought using coupons/vouchers"
label variable prop_credit "Proportion of improved seeds bought using credit"
label variable prop_left_seeds "Proportion of the seeds that come from left over's of the previous season"
label variable advice "Obtained agriculture advice"
label variable prop_free "Obtained agriculture advice"
label variable total_yield_projects "Amount of projects for yield increase in comm"
label variable total_imp_projects "Amount of projects for improved seeds in comm"
label variable assistant_ag_officer "Does an Assist. Agricultural Extension Development Officer live in this community?"
label variable maize_hybrid_sellers "Number of sellers of hybrid maize seed in the community"
label variable proportion_cover "Proportion of seeds that when planted there had cover before"
label variable prop_sandy "Proportion of sandy plots"
label variable prop_between "Proportion of plots with between soil type"
label variable prop_clay "Proportion of clay plots"
label variable prop_other "Proportion of other soil types"
label variable prop_good "Proportion of plots with good condition"
label variable prop_fair "Proportion of plots with fair condition"
label variable prop_poor "Proportion of plots with poor condition"
label variable prop_flat "Proportion of flat terrain"
label variable prop_slight "Proportion of slight slope terrain"
label variable prop_moderate "Proportion of moderate slope terrain"
label variable prop_steep "Proportion of steep terrain"
label variable prop_divert_stream "Proportion of plots with divert stream irrigation"
label variable prop_bucket "Proportion of plots with bucket irrigation"
label variable prop_hand_pump "Proportion of plots with hand pump irrigation"
label variable prop_treadle_pump "Proportion of plots with treadle pump irrigation"
label variable prop_motor_pump "Proportion of plots with motor pump irrigation"
label variable prop_gravity "Proportion of plots with gravity irrigation"
label variable prop_rainfed "Proportion of rainfed plots"
label variable prop_other_ "Proportion of plots with other irrigation method"
label variable prop_can_irrigation "Proportion of plots with can irrigation"
label variable prop_no_erosion "Proportion of plots with no erosion"
label variable prop_low_erosion "Proportion of plots with low erosion"
label variable prop_moderate_erosion "Proportion of plots with moderate erosion"
label variable prop_high_erosion "Proportion of plots with high erosion"
label variable prop_terrain "Proportion of plots with terrain constraints"
label variable prop_flooding "Proportion of plots affected by flooding"
label variable prop_wind "Proportion of plots affected by wind"
label variable prop_animals "Proportion of plots affected by animals"
label variable prop_other_constraint "Proportion of plots with other constraints"
label variable prop_no_erosion_control "Proportion of plots with no erosion control"
label variable prop_terraces "Proportion of plots with terraces for erosion control"
label variable prop_erosion_bunds "Proportion of plots with erosion control bunds"
label variable prop_gabions_sandbags "Proportion of plots with gabions or sandbags"
label variable prop_vetiver_grass "Proportion of plots with vetiver grass for erosion control"
label variable prop_tree_belts "Proportion of plots with tree belts for erosion control"
label variable prop_water_harvest_bunds "Proportion of plots with water harvest bunds"
label variable prop_drainage_ditches "Proportion of plots with drainage ditches"
label variable prop_other_erosion_control "Proportion of plots with other erosion control methods"
label variable prop_swamp "Proportion of swamp plots"

order case_id ea_id hh_improved HH_head_fem HH_head_age HH_head_salaried_emp education_1 education_2 education_3 education_4 education_5 education_6 education_7


save "$input/MWI_final.dta", replace




use "$input/MWI_final.dta", clear






























