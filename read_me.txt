#In order to reproduce the figures in the paper please run:

python EVEN_300_300_GENE_TOGETHER_SELECTIVE.py; python ODD_300_300_GENE_TOGETHER_SELECTIVE.py; python FULL_300_300_GENE_TOGETHER_SELECTIVE.py

#to reproduce figures from the suplementary please run:

python EVEN_1500_300_GENE_SEPERATE_SELECTIVE.py; python ODD_1500_300_GENE_SEPERATE_SELECTIVE.py; python FULL_1500_300_GENE_SEPERATE_SELECTIVE.py

python EVEN_1500_1500_TSS_SEPERATE_SELECTIVE.py; python ODD_1500_1500_TSS_SEPERATE_SELECTIVE.py; python FULL_1500_1500_TSS_SEPERATE_SELECTIVE.py

python AP_CLUSTERING_REPRODUCE.py #choose the option to plot/cluster. After plotting/clustering all options you can run TF_enrichments

#to cluster time series run 
python clustering_figures.py

#In order to produce the figures from the thesis please run the scripts above as well as:

#analysis for model trained on data from all enhancers

GAUSSIAN_300_300_GENE_TOGETHER_DYSTANCE.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_1.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_1_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_1_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_2_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_2_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_3_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_3_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_4.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_4_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_4_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_5.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_5_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_ALL_5_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_CONVERGENCE_CHECKER_1.py

python GAUSSIAN_EVEN_300_300_GENE_TOGETHER_SELECTIVE_ALL.py
python GAUSSIAN_ODD_300_300_GENE_TOGETHER_SELECTIVE_ALL.py


#analysis for model trained only on interacting enhancers

GAUSSIAN_300_300_GENE_TOGETHER_DYSTANCE.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_1.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_1_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_1_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_2_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_2_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_3_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_3_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_4.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_4_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_4_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_5.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_5_2.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING_5_3.py
GAUSSIAN_300_300_GENE_TOGETHER_SELECTIVE_CONVERGENCE_CHECKER_2.py

python GAUSSIAN_EVEN_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING.py
python GAUSSIAN_ODD_300_300_GENE_TOGETHER_SELECTIVE_INTERACTING.py
