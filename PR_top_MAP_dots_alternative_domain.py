def execute(sensitivity_match_MAP, number_of_interacting_enhancers_):

	#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
	from matplotlib.backends.backend_pdf import PdfPages
	import config_variables
	pdf = PdfPages('multipage_priors_{0}_{1}_20k_{2}_{3}_average.pdf'.format(config_variables.chroms_in_prior[0], config_variables.chroms_to_infer[0], config_variables.one_sided_or_two_sided, config_variables.use_smooth_prior_for_estimation))
	np = config_variables.np
	negative_interactions = config_variables.negative_interactions

	def extract_TSS_coordinates(upstream):

		data = np.loadtxt(config_variables.name_of_time_series_promoter_file_for_TSS_start, dtype = str,  delimiter = '\t')	
		plus_strand = data[:, 4] == '+'
		TSS_coordinates = np.zeros(len(plus_strand), int)
		TSS_coordinates[plus_strand] = data[plus_strand, 1].astype(int) + upstream
		TSS_coordinates[np.invert(plus_strand)] = data[np.invert(plus_strand), 2].astype(int) + upstream

		return TSS_coordinates

	TSS_coordinates = extract_TSS_coordinates(config_variables.upstream)

	def positive_negative_interactions_for_MAP(chrom):
		
		indexes_p, indexes_e, total_p, total_e = negative_interactions.initialise_variables(chrom)[2:]

		if mode == "promoter_enhancer_interactions":

			false_inter_pro = negative_interactions.chrom_specific_negative_interactions(chrom, mode)

			i_s_f, j_s_f = false_inter_pro[:,0] + total_p, false_inter_pro[:,1] + total_e

		if mode == "enhancer_enhancer_interactions":

			false_inter_enh = negative_interactions.chrom_specific_negative_interactions(chrom, mode)
	
			i_s_f, j_s_f = false_inter_enh[:,0] + total_e, false_inter_enh[:,1] + total_e

		return i_s_f, j_s_f


	def filter_interactions_in_domain(posterior_t, posterior_f, chrom, domain, invert_domain):
		enh_coordinates, pro_coordinates, indexes_p, indexes_e, total_p, total_e = negative_interactions.initialise_variables(chrom)

		i_s_f, j_s_f = positive_negative_interactions_for_MAP(chrom)
		
		length_chr = len(indexes_p) + len(indexes_e)
		interaction_matrix = np.zeros((length_chr, length_chr))
		posterior_t, posterior_f = posterior_t[chrom], posterior_f[chrom]
		
		if domain:
			if config_variables.TSS_or_intra_genic_for_domain_filter == "Intra_genic": coords_pro_domain = pro_coordinates[indexes_p]
			elif config_variables.TSS_or_intra_genic_for_domain_filter == "TSS_only": coords_pro_domain = np.column_stack((TSS_coordinates[indexes_p]-1, TSS_coordinates[indexes_p]+1))
			domain_matrix = interacting_domain.interacting_domains(coords_pro_domain, enh_coordinates[indexes_e], chrom, 'left', True)
			domain_matrix = domain_matrix + interacting_domain.interacting_domains(coords_pro_domain, enh_coordinates[indexes_e], chrom, 'right', True)
			if invert_domain: domain_matrix = np.invert(domain_matrix)

		else:
			domain_matrix = True

			
		if mode == "promoter_enhancer_interactions":

			chr_interactions_dict_pro_enh = config_variables.chr_interactions_dict_pro_enh
			true_inter_pro = un_string(chr_interactions_dict_pro_enh[chrom][:, :2]).astype(int)
			i_s_t, j_s_t = true_inter_pro[:,0], true_inter_pro[:,1]

			interaction_matrix[i_s_t - total_p, j_s_t + len(indexes_p) - total_e] = posterior_t
			interaction_matrix[i_s_f - total_p, j_s_f + len(indexes_p) - total_e] = posterior_f

			interacting_mask = np.zeros_like(interaction_matrix).astype(bool)
			interacting_mask[i_s_t - total_p, j_s_t + len(indexes_p) - total_e] = True

			true_pro_enh_inter_filtered = interacting_mask * domain_matrix

			print np.sum(true_pro_enh_inter_filtered)

			chrom_posterior_t_filtered = interaction_matrix[true_pro_enh_inter_filtered]

			interacting_mask = np.zeros_like(interaction_matrix).astype(bool)
			interacting_mask[i_s_f - total_p, j_s_f + len(indexes_p) - total_e] = True

			false_pro_enh_inter_filtered = interacting_mask * domain_matrix

			print np.sum(false_pro_enh_inter_filtered)

			chrom_posterior_f_filtered = interaction_matrix[false_pro_enh_inter_filtered]

			return	chrom_posterior_t_filtered, chrom_posterior_f_filtered

		if mode == "enhancer_enhancer_interactions":

			chr_interactions_dict_enh_enh = config_variables.chr_interactions_dict_enh_enh
			true_inter_enh = un_string(chr_interactions_dict_enh_enh[chrom][:, :2]).astype(int)
			i_s_t, j_s_t = true_inter_enh[:,0], true_inter_enh[:,1]

			
			interaction_matrix[i_s_t + len(indexes_p) - total_e, j_s_t + len(indexes_p) - total_e] = posterior_t
			interaction_matrix[i_s_f + len(indexes_p) - total_e, j_s_f + len(indexes_p) - total_e] = posterior_f
			interaction_matrix[j_s_t + len(indexes_p) - total_e, i_s_t + len(indexes_p) - total_e] = posterior_t # transpose to create a full matrix
			interaction_matrix[j_s_f + len(indexes_p) - total_e, i_s_f + len(indexes_p) - total_e] = posterior_f # transpose to create a full matrix


			interacting_mask = np.zeros_like(interaction_matrix).astype(bool)
			interacting_mask[i_s_t + len(indexes_p) - total_e, j_s_t + len(indexes_p) - total_e] = True

			true_enh_enh_inter_filtered = interacting_mask * domain_matrix
			chrom_posterior_t_filtered = interaction_matrix[true_enh_enh_inter_filtered]

			interacting_mask = np.zeros_like(interaction_matrix).astype(bool)
			interacting_mask[i_s_f + len(indexes_p) - total_e, j_s_f + len(indexes_p) - total_e] = True

			false_enh_enh_inter_filtered = interacting_mask * domain_matrix
			chrom_posterior_f_filtered = interaction_matrix[false_enh_enh_inter_filtered]
			
			return chrom_posterior_t_filtered, chrom_posterior_f_filtered


	

	from  prepare_interactions_clean import un_string
	normalised = False
	import interacting_domain
	import itertools

	def domain_filter(inpu, domain, invert_domain):

		posterior_t, posterior_f = inpu 
		chrom_posterior_t_filtered, chrom_posterior_f_filtered = {}, {}
		for chrom__ in chroms_to_infer:
			chrom_posterior_t_filtered[chrom__], chrom_posterior_f_filtered[chrom__] = filter_interactions_in_domain(posterior_t, posterior_f, chrom__, domain, invert_domain)

		posterior_t_filtered = np.array(list(itertools.chain.from_iterable([chrom_posterior_t_filtered[chrom_] for chrom_ in chroms_to_infer])))
		posterior_f_filtered = np.array(list(itertools.chain.from_iterable([chrom_posterior_f_filtered[chrom_] for chrom_ in chroms_to_infer])))
	
		return posterior_t_filtered, posterior_f_filtered
	#----------------------------------------------------------------------------------------------------------------------------------------------------------------------	


	import itertools
	import matplotlib.pyplot as plt
	import config_variables
	np = config_variables.np	
	classificator_elements = config_variables.classificator_elements
	classifiers_clean = config_variables.classifiers_clean
	filter_values = config_variables.filter_values
	datasets_names = config_variables.datasets_names
	chroms_to_infer = config_variables.chroms_to_infer
	mode = 	config_variables.mode
	plt.rcParams['xtick.labelsize'] = 24.
	plt.rc('ytick', labelsize=20)	

	
	#dict_option = {0: 'Pol2_2012-03', 1: 'Pol2',  2: 'H2AZ', 3: 'ER', 4: 'H3K4me3', 5: '2012-03_RNA', 6: 'RNA'}
	dict_option = dict(zip(range(len(datasets_names)), datasets_names))

	def calculate_single_ROC_best_True_sensitivity(probabilities_true, probabilities_false, length_of_positives, length_of_negatives, percent_1, percent_2, percent_3, thresh = False, give_indexes_for_thresholds = False):

		_True_positives_of_threshold = []
		_False_positives_of_threshold = []

		sorted_prob_true = np.sort(probabilities_true)
		sorted_prob_false = np.sort(probabilities_false)

		sorted_thresholds = np.sort(np.unique(np.r_[probabilities_true, probabilities_false]))
		sorted_thresholds = np.unique(np.r_[sorted_thresholds, np.max(sorted_thresholds)*1.01])

		len_prob_true = len(probabilities_true)
		len_prob_false = len(probabilities_false)

		print 'len prob: ', len_prob_true, len_prob_false

		_True_positives_of_threshold = np.cumsum(np.histogram(sorted_prob_true, sorted_thresholds)[0][::-1])

		_False_positives_of_threshold = np.cumsum(np.histogram(sorted_prob_false, sorted_thresholds)[0][::-1])

		Precision = np.array(_True_positives_of_threshold, dtype = float)/(np.array(_True_positives_of_threshold, dtype = float) + np.array(_False_positives_of_threshold, dtype = float))
	
		True_positive_Rate = np.array(_True_positives_of_threshold)/float(len_prob_true)#float(length_of_positives)#
		
		False_positive_Rate = np.array(_False_positives_of_threshold)/float(len_prob_false)#float(length_of_negatives)#


		if give_indexes_for_thresholds:

			threshold_1, threshold_2, threshold_3 = percent_1, percent_2, percent_3
			index_100_first_occurance =	np.where(sorted_thresholds[::-1] <= threshold_1)[0][0] - 1
			index_200_first_occurance = np.where(sorted_thresholds[::-1] <= threshold_2)[0][0] - 1
			index_300_first_occurance = np.where(sorted_thresholds[::-1] <= threshold_3)[0][0] - 1



			threshold_1, threshold_2, threshold_3 = [], [], []
			return True_positive_Rate, False_positive_Rate, Precision, index_100_first_occurance, index_200_first_occurance, index_300_first_occurance, threshold_1, threshold_2, threshold_3

		else:

			index_100_first_occurance = np.where(True_positive_Rate >= percent_1)[0][0]
			index_200_first_occurance = np.where(True_positive_Rate >= percent_2)[0][0]
			index_300_first_occurance = np.where(True_positive_Rate >= percent_3)[0][0]

			#print "Precision", Precision[:40], "TPR", True_positive_Rate[:40], "number of features above FDR:", np.where(Precision >= 0.80)[0][-1], Precision[Precision >= 0.80][-1], _True_positives_of_threshold[Precision >= 0.80][-1]
			#var = raw_input("Please enter something (pause): ")


		if thresh:
			threshold_1 = sorted_thresholds[::-1][index_100_first_occurance + 1]
			threshold_2 = sorted_thresholds[::-1][index_200_first_occurance + 1]
			threshold_3 = sorted_thresholds[::-1][index_300_first_occurance + 1]
			return True_positive_Rate, False_positive_Rate, Precision, index_100_first_occurance, index_200_first_occurance, index_300_first_occurance, threshold_1, threshold_2, threshold_3
	
		#print 'number of thresholds', len(True_positive_Rate), len(False_positive_Rate)

		#return True_positive_Rate, False_positive_Rate, Precision, index_100_first_occurance, index_200_first_occurance, index_300_first_occurance


	from pylab import rcParams
	rcParams['figure.figsize'] = 20, 8

	#stuff = [0, 1, 2, 3, 4]

	stuff = [1, 2, 3, 4]
	#stuff = [0, 2, 3, 4]
	combinations = []


	filter_values_ = filter_values[[0]]


	for L in range(0, len(stuff)+1):
		for subset in itertools.combinations(stuff, L):
			if len(subset): combinations += [list(subset)]

	#option_ = combinations[-1]
	#filter_value = -1.
	#selected_combinations = [combinations[ind] for ind in [0, 1, 3, 5, 7, 10, 16]]

	selected_combinations = np.array(combinations)[[0, 2, 5, 10, 14]].tolist()

	#selected_combinations = combinations


	#selected_combinations = [[0], [1], [3], [0,1], [0,3], [1,3], [0,1,3]]

	#http://stackoverflow.com/questions/14270391/python-matplotlib-multiple-bars - alternatively
	#http://matplotlib.org/examples/pylab_examples/subplots_demo.html


	percent_1_, percent_2_, percent_3_ = 0.1, 0.2, 0.3

	dict_option_ = dict_option
	datasets_names_ = datasets_names

	threshold_1_dist_correl, threshold_2_dist_correl, threshold_3_dist_correl = {}, {}, {}
	threshold_1_correl, threshold_2_correl, threshold_3_correl = {}, {}, {}
	threshold_1_dist, threshold_2_dist, threshold_3_dist = {}, {}, {}
	if config_variables.MoG_classificator: threshold_1_dist_correl_MOG, threshold_2_dist_correl_MOG, threshold_3_dist_correl_MOG = {}, {}, {}

	total_number_of_interacting_enhancers = config_variables.total_number_of_interacting_enhancers

	for domain_atr, domain, invert_domain, thresh, give_indexes_for_thresholds in [[None, False, False, True, False], ["within_domain", True, False, False, True], ["outside_domain", True, True, False, True]]:

		f, ax = plt.subplots(len(filter_values_), len(selected_combinations), sharex=True, sharey=True)
		#ax[0,0].plot(x, y)
		#f.subplots_adjust(hspace=0.1)
		#f.subplots_adjust(wspace=0.1)
		f.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, hspace=0.1, wspace=0.1)


		for index_filt_val, filter_value in enumerate(filter_values_):

			posterior_dist_true, posterior_dist_false = domain_filter(classifiers_clean.posterior_producer([0], [], total_posterior = False), domain, invert_domain)



			#posterior_dist_true, posterior_dist_false = np.array(posterior_dist_true), np.array(posterior_dist_false)
			#posterior_dist_true, posterior_dist_false = posterior_dist_true[posterior_dist_true <> 1.], posterior_dist_false[posterior_dist_false <> 1.]

			for index_opt, option_ in enumerate(selected_combinations):
	
				comb = ",".join([dict_option_[el] for el in option_])
				if option_ == combinations[-1]: comb = "All"
				print comb

				if domain_atr <> None:
					number_of_interacting_enhancers = total_number_of_interacting_enhancers[domain_atr]
					sensitivity_dist_correl = sensitivity_match_MAP["correl_dist"][domain_atr][",".join(np.array(option_, str))]
					sensitivity_correl = sensitivity_match_MAP["correl"][domain_atr][",".join(np.array(option_, str))]
					sensitivity_dist = sensitivity_match_MAP["dist"][domain_atr][",".join(np.array(option_, str))]

				else:
					number_of_interacting_enhancers = number_of_interacting_enhancers_
					sensitivity_dist_correl = sensitivity_match_MAP["correl_dist"][",".join(np.array(option_, str))]
					sensitivity_correl = sensitivity_match_MAP["correl"][",".join(np.array(option_, str))]
					sensitivity_dist = sensitivity_match_MAP["dist"][",".join(np.array(option_, str))]


				full_len = sum([len(classificator_elements[-1.][mode]["positive_interactions"]["distance"]["probabilities_of_being_positive_interactions"]["posterior_component_values"][chrom_]) for chrom_ in chroms_to_infer])
				new_len = sum([len(classificator_elements[filter_value][mode]["positive_interactions"]["distance"]["probabilities_of_being_positive_interactions"]["posterior_component_values"][chrom_]) for chrom_ in chroms_to_infer])

				length_of_positives_pro = full_len
				length_of_negatives_pro = sum([len(classificator_elements[-1.][mode]["negative_interactions"]["distance"]["probabilities_of_being_positive_interactions"]["posterior_component_values"][chrom_]) for chrom_ in chroms_to_infer])
				#full_len = len(true_interactions_dist_correl_pairwise_prob_pro_filter_comb[-1.])
				#new_len = len(true_interactions_dist_correl_pairwise_prob_pro_filter_comb[filter_value])

				per = float(full_len)/float(new_len)
				percent_1 = percent_1_ * per
				percent_2 = percent_2_ * per
				percent_3 = percent_3_ * per

				posterior_correl_dist_true, posterior_correl_dist_false = domain_filter(classifiers_clean.posterior_producer([0], option_, total_posterior = False), domain, invert_domain)
				posterior_correl_true, posterior_correl_false = domain_filter(classifiers_clean.posterior_producer([], option_, total_posterior = False), domain, invert_domain)

				
				if config_variables.MoG_classificator:posterior_correl_dist_true_MOG, posterior_correl_dist_false_MOG = domain_filter(classifiers_clean.MOG_classifier(option_, total_posterior = False), domain, invert_domain)

				#posterior_correl_dist_true, posterior_correl_dist_false = np.array(posterior_correl_dist_true), np.array(posterior_correl_dist_false)
				#posterior_correl_true, posterior_correl_false = np.array(posterior_correl_true), np.array(posterior_correl_false)

				#posterior_correl_dist_true, posterior_correl_dist_false = posterior_correl_dist_true[posterior_correl_dist_true <> 1.], posterior_correl_dist_false[posterior_correl_dist_false <> 1.]

				#posterior_correl_true, posterior_correl_false = posterior_correl_true[posterior_correl_true <> 1.], posterior_correl_false[posterior_correl_false <> 1.]
				#print option_


				if give_indexes_for_thresholds: 
					percent_1, percent_2, percent_3 = threshold_1_dist_correl[comb], threshold_2_dist_correl[comb], threshold_3_dist_correl[comb]

				
				True_positive_Rate_dist_correl_pro, False_positive_Rate_dist_correl_pro, precision_dist_correl_pro, index_100_dist_correl_pro, index_200_dist_correl_pro, index_300_dist_correl_pro, threshold_1_dist_correl_, threshold_2_dist_correl_, threshold_3_dist_correl_ = calculate_single_ROC_best_True_sensitivity(posterior_correl_dist_true, posterior_correl_dist_false, length_of_positives_pro, length_of_negatives_pro, percent_1, percent_2, percent_3, thresh = thresh, give_indexes_for_thresholds = give_indexes_for_thresholds)

				if give_indexes_for_thresholds: 
					percent_1, percent_2, percent_3 = threshold_1_dist[comb], threshold_2_dist[comb], threshold_3_dist[comb]

				True_positive_Rate_dist_pro, False_positive_Rate_dist_pro, precision_dist_pro, index_100_dist_pro, index_200_dist_pro, index_300_dist_pro, threshold_1_dist_, threshold_2_dist_, threshold_3_dist_ = calculate_single_ROC_best_True_sensitivity(posterior_dist_true, posterior_dist_false, length_of_positives_pro, length_of_negatives_pro, percent_1, percent_2, percent_3, thresh = thresh, give_indexes_for_thresholds = give_indexes_for_thresholds)

				if give_indexes_for_thresholds: 
					percent_1, percent_2, percent_3 = threshold_1_correl[comb], threshold_2_correl[comb], threshold_3_correl[comb]

				True_positive_Rate_correl_pro, False_positive_Rate_correl_pro, precision_correl_pro, index_100_correl_pro, index_200_correl_pro, index_300_correl_pro, threshold_1_correl_, threshold_2_correl_, threshold_3_correl_ = calculate_single_ROC_best_True_sensitivity(posterior_correl_true, posterior_correl_false, length_of_positives_pro, length_of_negatives_pro, percent_1, percent_2, percent_3, thresh = thresh, give_indexes_for_thresholds = give_indexes_for_thresholds)


				#MOG--------------------------
				if config_variables.MoG_classificator:
					if give_indexes_for_thresholds: 
						percent_1, percent_2, percent_3 = threshold_1_dist_correl_MOG[comb], threshold_2_dist_correl_MOG[comb], threshold_3_dist_correl_MOG[comb]
				
					True_positive_Rate_dist_correl_pro_MOG, False_positive_Rate_dist_correl_pro_MOG, precision_dist_correl_pro_MOG, index_100_dist_correl_pro_MOG, index_200_dist_correl_pro_MOG, index_300_dist_correl_pro_MOG, threshold_1_dist_correl_MOG_, threshold_2_dist_correl_MOG_, threshold_3_dist_correl_MOG_ = calculate_single_ROC_best_True_sensitivity(posterior_correl_dist_true_MOG, posterior_correl_dist_false_MOG, length_of_positives_pro, length_of_negatives_pro, percent_1, percent_2, percent_3, thresh = thresh, give_indexes_for_thresholds = give_indexes_for_thresholds)


				if thresh: 

					threshold_1_dist_correl[comb], threshold_2_dist_correl[comb], threshold_3_dist_correl[comb] = threshold_1_dist_correl_, threshold_2_dist_correl_, threshold_3_dist_correl_
					threshold_1_dist[comb], threshold_2_dist[comb], threshold_3_dist[comb] = threshold_1_dist_, threshold_2_dist_, threshold_3_dist_
					threshold_1_correl[comb], threshold_2_correl[comb], threshold_3_correl[comb] = threshold_1_correl_, threshold_2_correl_, threshold_3_correl_
					if config_variables.MoG_classificator: threshold_1_dist_correl_MOG[comb], threshold_2_dist_correl_MOG[comb], threshold_3_dist_correl_MOG[comb] = threshold_1_dist_correl_MOG_, threshold_2_dist_correl_MOG_, threshold_3_dist_correl_MOG_

				centres_of_ticks = np.arange(4) + 0.5
				ind = centres_of_ticks

				OX = [0.1,"0.2\n TPR ",0.3, "\nMAP"]

			
				#plt.xlabel('TPR-recall')
				#plt.ylabel('Precision')
				marker_size = 12

				if len(filter_values_) == 1:

					#ax[index_opt].bar(ind, np.r_[precision_dist_correl_pro[[index_100_dist_correl_pro, index_200_dist_correl_pro, index_300_dist_correl_pro]], sensitivity_match_MAP["correl_dist"][",".join(np.array(option_, str))]], width=width,  alpha=0.2, color="blue")
					#ax[index_opt].bar(ind, np.r_[precision_dist_pro[[index_100_dist_pro, index_200_dist_pro, index_300_dist_pro]], sensitivity_match_MAP["dist"][",".join(np.array(option_, str))]], alpha=0.2, width=width,color="yellow")
					#ax[index_opt].bar(ind, np.r_[precision_correl_pro[[index_100_correl_pro, index_200_correl_pro, index_300_correl_pro]], sensitivity_match_MAP["correl"][",".join(np.array(option_, str))]], width=width,alpha=0.2, color="red")

				
					probabilities_dist_correl = np.r_[precision_dist_correl_pro[[index_100_dist_correl_pro, index_200_dist_correl_pro, index_300_dist_correl_pro]], sensitivity_dist_correl]
					n = np.r_[np.array([True_positive_Rate_dist_correl_pro[index_100_dist_correl_pro], True_positive_Rate_dist_correl_pro[index_200_dist_correl_pro], True_positive_Rate_dist_correl_pro[index_300_dist_correl_pro]])*number_of_interacting_enhancers_, number_of_interacting_enhancers_]
					yerr = (probabilities_dist_correl*(1-probabilities_dist_correl)/n)**0.5
					ax[index_opt].errorbar(ind, probabilities_dist_correl, yerr= yerr, fmt='^', color="b", alpha=0.5, linewidth=3., markersize=marker_size)
					ax[index_opt].plot(ind, probabilities_dist_correl, alpha=1.0, color="b", marker= "^", linewidth=0.0, markersize=marker_size, label = "data + distance")

					probabilities_dist = np.r_[precision_dist_pro[[index_100_dist_pro, index_200_dist_pro, index_300_dist_pro]], sensitivity_dist]
					n = np.r_[np.array([True_positive_Rate_dist_pro[index_100_dist_pro], True_positive_Rate_dist_pro[index_200_dist_pro], True_positive_Rate_dist_pro[index_300_dist_pro]])*number_of_interacting_enhancers_, number_of_interacting_enhancers_]
					yerr = (probabilities_dist*(1-probabilities_dist)/n)**0.5
					ax[index_opt].errorbar(ind, probabilities_dist, yerr = yerr, fmt='s', color="y", alpha=0.5, linewidth=3., markersize=marker_size)
					ax[index_opt].plot(ind, probabilities_dist, alpha=1.0, color="y", marker= "s", linewidth=0.0, markersize=marker_size, label = "distance")

					probabilities_correl = np.r_[precision_correl_pro[[index_100_correl_pro, index_200_correl_pro, index_300_correl_pro]], sensitivity_correl]
					n = np.r_[np.array([True_positive_Rate_correl_pro[index_100_correl_pro], True_positive_Rate_correl_pro[index_200_correl_pro], True_positive_Rate_correl_pro[index_300_correl_pro]])*number_of_interacting_enhancers_, number_of_interacting_enhancers_]
					yerr = (probabilities_correl*(1-probabilities_correl)/n)**0.5
					ax[index_opt].errorbar(ind, probabilities_correl, yerr= yerr, fmt='o', color="red", alpha=0.5, linewidth=3., markersize=marker_size)
					ax[index_opt].plot(ind, probabilities_correl, alpha=1.0, color="red", marker= "o", linewidth=0.0, markersize=marker_size, label = "data")

					#-------------------------MOG
					if config_variables.MoG_classificator:
						probabilities_dist_correl_MOG = precision_dist_correl_pro[[index_100_dist_correl_pro_MOG, index_200_dist_correl_pro_MOG, index_300_dist_correl_pro_MOG]]#, sensitivity_dist_correl]
						n = np.array([True_positive_Rate_dist_correl_pro_MOG[index_100_dist_correl_pro_MOG], True_positive_Rate_dist_correl_pro_MOG[index_200_dist_correl_pro_MOG], True_positive_Rate_dist_correl_pro_MOG[index_300_dist_correl_pro_MOG]])*number_of_interacting_enhancers_
						yerr = (probabilities_dist_correl_MOG*(1-probabilities_dist_correl_MOG)/n)**0.5
						ax[index_opt].errorbar(ind[:-1], probabilities_dist_correl_MOG, yerr= yerr, fmt='*', color="cyan", alpha=0.5, linewidth=3., markersize=marker_size)
						ax[index_opt].plot(ind[:-1], probabilities_dist_correl_MOG, alpha=1.0, color="cyan", marker= "*", linewidth=0.0, markersize=marker_size, label = "MOG")





					#[index_opt].plot(ind, np.r_[precision_correl_pro[[index_100_correl_pro, index_200_correl_pro, index_300_correl_pro]], sensitivity_match_MAP["correl"][",".join(np.array(option_, str))]], alpha=1.0, color="red", marker= "o", linewidth=0.0)

					ax[index_opt].vlines(3., 0, 1, colors=u'SlateGray', linestyles=u'dashed')
					ax[index_opt].set_xlim([0., 4.])
					ax[index_opt].set_ylim([0., 1.])

					ax[index_opt].set_xticks(centres_of_ticks)
					ax[index_opt].set_xticklabels(np.array(OX, str))

					if index_filt_val == 0: ax[index_opt].set_title(comb, fontsize=26)
					if index_opt == 0:
		
						ax[index_opt].set_ylabel('Precision', fontsize=26)
						import matplotlib.lines as mlines
						blue_line = mlines.Line2D([], [], color='blue', marker='^', markersize=20, label='data + prior')
						yellow_line = mlines.Line2D([], [], color='yellow', marker='s', markersize=20, label='prior')
						red_line = mlines.Line2D([], [], color='red', marker='o', markersize=20, label='data')
						pink_line = mlines.Line2D([], [], color='cyan', marker='*', markersize=20, label='MOG')
						#ax[index_opt].legend(handles=[blue_line, yellow_line, red_line])
						#ax.get_legend_handles_labels()
						handles, labels = ax[index_opt].get_legend_handles_labels()
						ax[index_opt].legend(handles, labels, fontsize=22)
				else:

					ax[index_filt_val, index_opt].bar(ind, precision_dist_correl_pro[[index_100_dist_correl_pro, index_200_dist_correl_pro, index_300_dist_correl_pro]], width=width,  alpha=0.2, color="blue")
					ax[index_filt_val, index_opt].bar(ind, precision_dist_pro[[index_100_dist_pro, index_200_dist_pro, index_300_dist_pro]], alpha=0.2, width=width,color="yellow")
					ax[index_filt_val, index_opt].bar(ind, precision_correl_pro[[index_100_correl_pro, index_200_correl_pro, index_300_correl_pro]], width=width,alpha=0.2, color="red")
					ax[index_filt_val, index_opt].set_xlim([0., 3.])
					ax[index_filt_val, index_opt].set_ylim([0., 1.])



					ax[index_filt_val, index_opt].set_xticks(np.arange(3)+0.5)
					ax[index_filt_val, index_opt].set_xticklabels(np.array(OX, str))



					if index_filt_val == 0: ax[index_filt_val, index_opt].set_title(comb, fontsize=12)
					if index_opt == 0: ax[index_filt_val, index_opt].set_ylabel(str(filter_value), fontsize=12)


			pdf.savefig()
	pdf.close()	
	plt.show()



