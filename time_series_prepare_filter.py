import numpy as np
import config_variables
data_folder = config_variables.data_folder

def time_series_prepare(name_of_pro_dataset_to_open, name_of_enh_dataset_to_open):
	
	dataset_time_series_dict = {}
	
	list_of_datasets = list(name_of_enh_dataset_to_open) + list(name_of_pro_dataset_to_open)

	import config_variables
	data_folder = config_variables.data_folder

	for name_of_dataset_to_open, norm_name in zip(list_of_datasets, list(datasets_names)*2):

		norm_n = np.loadtxt(data_folder + '{0}_normalising_constants.gz'.format(norm_name), dtype = float, usecols=(0,))[:time_points]
		
		dataset_time_series = np.loadtxt(name_of_dataset_to_open, dtype = str, delimiter = '\t')

		dataset_time_series_dict[name_of_dataset_to_open] = [dataset_time_series[:, 0], dataset_time_series[:, [1,2]].astype(float), dataset_time_series[:, 3:][:, :time_points].astype(float)/norm_n*norm_n[0]]

	return dataset_time_series_dict


def time_series_prepare_mean_std(name_of_pro_dataset_to_open, name_of_enh_dataset_to_open):
	
	dataset_time_series_dict_mean_std = {}
	
	list_of_datasets = list(name_of_enh_dataset_to_open) + list(name_of_pro_dataset_to_open)

	for name_of_dataset_to_open, norm_name in zip(list_of_datasets, list(datasets_names)*2):

		norm_n = np.loadtxt(data_folder + '{0}_normalising_constants.gz'.format(norm_name), dtype = float, usecols=(0,))[:time_points]
		
		dataset_time_series = np.loadtxt(name_of_dataset_to_open, dtype = str, delimiter = '\t')

		time_series_count_norm = dataset_time_series[:, 3:][:, :time_points].astype(float)/norm_n

		time_series_std_mean_norm = (time_series_count_norm - time_series_count_norm.mean(1)[:,None])/time_series_count_norm.std(1)[:,None]

		dataset_time_series_dict_mean_std[name_of_dataset_to_open] = [dataset_time_series[:, 0], dataset_time_series[:, [1,2]].astype(float), time_series_std_mean_norm]

	return dataset_time_series_dict_mean_std


def time_series_prepare_concat(name_of_pro_dataset_to_open, name_of_enh_dataset_to_open, datasets_names_, dataset_time_series_dict, name_of_time_series_enhancer_file, name_of_time_series_promoter_file):
	
	def core(name, nameS_of_datasetS_to_open, datasets_names_, dataset_time_series_dict_):

		norm_total = []
		dataset_time_series_total = np.array([]).reshape(dataset_time_series_dict_[nameS_of_datasetS_to_open[0]][0].shape[0], 0)

		for name_of_dataset_to_open, norm_name in zip(list(nameS_of_datasetS_to_open), list(datasets_names_)):

			name = name + '_' + norm_name

			norm_n = np.loadtxt(data_folder + '{0}_normalising_constants.gz'.format(norm_name), dtype = float, usecols=(0,))[:time_points]
		
			dataset_time_series = np.loadtxt(name_of_dataset_to_open, dtype = str, delimiter = '\t')

			norm_total = np.r_[norm_total, norm_n]	

			dataset_time_series_total = np.c_[dataset_time_series_total, dataset_time_series[:, 3:][:, :time_points]]

		dataset_time_series_dict_[name] = [dataset_time_series[:, 0], dataset_time_series[:, [1,2]].astype(float), dataset_time_series_total.astype(float)/norm_total*norm_total[0]]

		return dataset_time_series_dict, name

	dataset_time_series_dict, name_enh = core(name_of_time_series_enhancer_file, name_of_enh_dataset_to_open, datasets_names_, dataset_time_series_dict)
	dataset_time_series_dict, name_pro = core(name_of_time_series_promoter_file, name_of_pro_dataset_to_open, datasets_names_, dataset_time_series_dict)

	return dataset_time_series_dict, name_enh, name_pro 


