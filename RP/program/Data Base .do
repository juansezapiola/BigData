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
*0) Key ID
*1) Identification of Improved seeds 
*2) HH Characteristics
*3) AGR Characteristics
*==============================================================================*


*0) Key ID
*==============================================================================*

*Creamos una base con los ID de los hogares del 2019.

use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_h.dta", clear

*Vemos si hay hogares duplicados 
bysort case_id: gen dup_count = _n
keep if dup_count==1


save "$input/key_id_2019.dta", replace

*8798 HH


*1) Identification of Improved seeds
*==============================================================================*

*Open seeds database.

use "/Users/juansegundozapiola/Documents/Maestria/Big Data/MWI_2019/ag_mod_h.dta", clear


codebook crop_code
label list ag_H_seed_roster__id

/* Improved seeds:
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

// Generate the new variable for each round
gen improved = .
    
// Replace the variable based on the values in seed_R
replace improved = 1 if inlist(crop_code, 3, 4, 12, 13, 14, 15, 18, 19, 20, 21, 24)
replace improved = 0 if improved==.

bysort case_id: gen n = _n
 
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
*/


keep case_id hh_improved

label variable hh_improved "Improved seed adoption (1: Adopted ; 0: No)"


save "$input/hh_improved.dta", replace



*2) HH Characteristics
*==============================================================================*









*3) AGR Characteristics
*==============================================================================*












