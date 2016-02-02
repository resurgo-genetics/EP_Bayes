import os
import shlex, subprocess
import numpy as np
import re

import config_variables

name_of_promoter_file_for_overlap = config_variables.name_of_promoter_file_for_overlap
name_of_enhancer_file_for_overlap = config_variables.name_of_enhancer_file_for_overlap


upstream = config_variables.upstream
downstream = 0

upstream_validation = config_variables.upstream
downstream_validation = config_variables.downstream

promoter_overlaps_enhancer_file = config_variables.promoter_overlaps_enhancer_file

disentagled_features_validation = config_variables.disentagled_features_validation

command_line = "windowBed -a {0} -b {1} -sw -l {2} -r {3} > {4}".format(name_of_promoter_file_for_overlap, name_of_enhancer_file_for_overlap, upstream, downstream, promoter_overlaps_enhancer_file)
os.system(command_line)

name_of_overlap_file_pro = config_variables.name_of_overlap_file_pro
name_of_overlap_file_enh = config_variables.name_of_overlap_file_enh

os.system("cut -f1-5 {0} > {1}".format(promoter_overlaps_enhancer_file, name_of_overlap_file_pro))
os.system("cut -f6-11 {0} > {1}".format(promoter_overlaps_enhancer_file, name_of_overlap_file_enh))

import non_ER_promoters_clean
import non_proximal_enhancer_clean

def extract_coordinates():

	data = np.loadtxt(config_variables.name_of_time_series_promoter_file_for_TSS_start, dtype = str,  delimiter = '\t')	
	plus_strand = data[:, 4] == '+'
	minus_strand = np.invert(plus_strand)

	promoter_data = np.zeros_like(data).astype(int)[:,:4]
	promoter_data[plus_strand, 1] = data[plus_strand, 1].astype(int) - upstream_validation
	promoter_data[plus_strand, 2] = data[plus_strand, 1].astype(int) + downstream_validation
	
	promoter_data[minus_strand, 2] = data[minus_strand, 2].astype(int) + upstream_validation
	promoter_data[minus_strand, 1] = data[minus_strand, 2].astype(int) - downstream_validation

	promoter_data = promoter_data.astype(str)
	promoter_data[:, 0] = data[:, 0]

	#--------------------
	ER_promoters = np.loadtxt("ER_controled_promoters_pindexed.txt", dtype = str, delimiter = '\t')
	Non_ER_promoters = np.loadtxt("Non_ER_controled_promoters_pindexed.txt", dtype = str, delimiter = '\t')
	def un_string(array_to_clean):  return np.array(map(lambda x: int(re.findall('\d+', x)[0]), array_to_clean))
	ER_promoters_indexes = un_string(ER_promoters[:, 3])

	ER_promoters_indexes_mask = np.zeros(len(data), bool)
	ER_promoters_indexes_mask[ER_promoters_indexes] = True 

	promoter_data[np.invert(ER_promoters_indexes_mask), 3] = Non_ER_promoters[:,-1]
	promoter_data[ER_promoters_indexes_mask, 3] = ER_promoters[:,-1]
	
	np.savetxt("ER_controled_promoters_pindexed_2.txt", promoter_data[ER_promoters_indexes_mask], fmt = "%s", delimiter = "\t")
	np.savetxt("Non_ER_controled_promoters_pindexed_2.txt", promoter_data[np.invert(ER_promoters_indexes_mask)], fmt = "%s", delimiter = "\t")

if disentagled_features_validation: 
	extract_coordinates()
	os.system("cat Non_ER_controled_promoters_pindexed_2.txt ER_controled_promoters_pindexed_2.txt distal_ER_peaks_pindexed.txt > all_features_without_distance_ones")
else:
	os.system("cat Non_ER_controled_promoters_pindexed.txt ER_controled_promoters_pindexed.txt distal_ER_peaks_pindexed.txt > all_features_without_distance_ones")

os.system("sort -k 1,1d -k 2,2n -k 3,3n all_features_without_distance_ones > all_features_without_distance_ones_s")

import orderer_clean
orderer_clean.executor("all_features_without_distance_ones_s", config_variables.chrom_names)

if disentagled_features_validation: 

	os.system("pairToBed -a merged_interactions_CHiA_PET_ordered_0_ind -b all_features_without_distance_ones_s_ordered -type both > all_features_s_ordered_concat_new_interactions_{0}_{1}_{2}_{3}".format(upstream, downstream, upstream_validation, downstream_validation))

	import interaction_checker_changed_clean
	interaction_checker_changed_clean.executor("all_features_s_ordered_concat_new_interactions_{0}_{1}_{2}_{3}".format(upstream, downstream, upstream_validation, downstream_validation), upstream_validation, downstream_validation)

else:
	os.system("pairToBed -a merged_interactions_CHiA_PET_ordered_0_ind -b all_features_without_distance_ones_s_ordered -type both > all_features_s_ordered_concat_new_interactions_{0}_{1}".format(upstream, downstream))

	import interaction_checker_changed_clean
	interaction_checker_changed_clean.executor("all_features_s_ordered_concat_new_interactions_{0}_{1}".format(upstream, downstream), upstream, downstream)

