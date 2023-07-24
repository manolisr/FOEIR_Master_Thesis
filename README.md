
## Abstract
Recommendations should serve the needs of all their partakers. Not only should they try
to maximize user’s utility, but also take responsibility for the notion of fairness they provide
towards the objects they rank. This work aims to capture the impact of F airness of Exposure
in Rankings framework as a bias mitigation and fairness of exposure allocation technique,
under a dynamic and implicit user feedback setting. To achieve this, two recommender system
pipelines are proposed. The one used as a baseline, generates its final recommendations solely
based on Bayesian P ersonalized Ranking. The second one, also employs FOEIR post-process
fairness recommendation algorithm. We observe, that although FOEIR mitigates various forms
of biases in the short run, past the 120th recommendation round mark, it overexposes popular
objects by 50% more on average, than the non-popular ones. Stricter constraints should be
adopted to ensure fairness on an object level, under a dynamic temporal recommendation
setting.

## Data Generation Instructions

![1](https://github.com/manolisr/FOEIR_Master_Thesis/assets/48391307/bfdd8c8c-b019-406c-8476-7afcc9eecf51)

For running librec-auto:

1. Install librec-auto: pip install librec-auto
2. Prepare your project structure as follows:
- In your current path, create ‘data’ and ‘demo’ directories: [/current_dir/]data and [/current_dir/]demo/conf
	- copy config.xml to [/current_dir/]demo/conf
	  copy the train-1.txt and test-1.txt files to [/current_dir/]data
3. run librec-auto from your [/current_dir/] directory: python -m librec_auto run -t demo -nj -nc

## Experiments

Generated data may represent any type of object being recommended to any subject. 
For convenience and explainability reasons, I refer to objects as items and to subjects as users. A movie recommendation scenario may be assumed. 
An overview of both recommendation pipelines operation and information flow is presented below.

### Baseline Librec-Auto Experiment

Base recommender pipeline, produces its final recommendations without using any algorithm that claims to offer a notion of fairness to the items it ranks. Thus, it aims to maximize user's utility. These results, are used as a baseline against FOEIR experiment suggestions. Figure 3.1 depicts the stream of information between pipeline's constituent parts.

![BASE_Flow](https://github.com/manolisr/FOEIR_Master_Thesis/assets/48391307/5c5f09af-4e14-42fc-b6e1-f8de76cf8bb5)


### Fairness of Exposure in Rankings Experiment

FOEIR Experiment pipeline, up to a certain degree follows the structure presented in the previous subsection with some key differences and some important additions. Primarily, Base Experiment's recommendations, alongside some further information discussed below, is used as input in the FOEIR post-process reranking algorithm. That way, final item to user recommendations are produced. FOEIR framework, tries to maximize user's utility, subject to a certain constraint that aims to alleviate the effects of various types of bias and provide a notion of fairness towards non - protected objects. Regarding the implementation, authors of the Fairness of Exposure in Rankings, work did not provide a repository with their implementation codebase. Versions of FOEIR algorithm may be found in online repositories (https://github.com/MilkaLichtblau/BA_Laura, https://github.com/jfinkels/birkhoff), but still further refinement was required to address this work needs.


![FOEIR_Flow](https://github.com/manolisr/FOEIR_Master_Thesis/assets/48391307/98917aa6-d39a-4057-a9e2-ebdc45814cc2)






