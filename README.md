[![Documentation Status](https://readthedocs.org/projects/pykg2vec/badge/?version=latest)](https://pykg2vec.readthedocs.io/en/latest/?badge=latest) [![CircleCI](https://circleci.com/gh/Sujit-O/pykg2vec.svg?style=svg)](https://circleci.com/gh/Sujit-O/pykg2vec) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![Build Status](https://travis-ci.org/Sujit-O/pykg2vec.svg?branch=master)](https://travis-ci.org/Sujit-O/pykg2vec) [![PyPI version](https://badge.fury.io/py/pykg2vec.svg)](https://badge.fury.io/py/pykg2vec) [![GitHub license](https://img.shields.io/github/license/Sujit-O/pykg2vec.svg)](https://github.com/Sujit-O/pykg2vec/blob/master/LICENSE) [![Coverage Status](https://coveralls.io/repos/github/Sujit-O/pykg2vec/badge.svg?branch=master)](https://coveralls.io/github/Sujit-O/pykg2vec?branch=master) [![Twitter](https://img.shields.io/twitter/url/https/github.com/Sujit-O/pykg2vec.svg?style=social)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FSujit-O%2Fpykg2vec) 

# Pykg2vec: Python Library for KGE Methods 
Pykg2vec is a library for learning the representation of entities and relations in Knowledge Graphs. We have attempted to bring state-of-the-art Knowledge Graph Embedding (KGE) algorithms and the necessary building blocks in the pipeline of knowledge graph embedding task into a single library. We hope Pykg2vec is both practical and educational for people who want to explore the related fields. For beginners, these papers, [A Review of Relational Machine Learning for Knowledge Graphs](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7358050), [Knowledge Graph Embedding: A Survey of Approaches and Applications](https://ieeexplore.ieee.org/document/8047276), and [An overview of embedding models of entities and relationships for knowledge base completion](https://arxiv.org/abs/1703.08098) can be good starting points! 
Pykg2vec has following features:
* Support state-of-the-art KGE model implementations and benchmark datasets. (also support custom datasets)
* Support automatic discovery for hyperparameters.
* Tools for inspecting the learned embeddings. 
  * Support exporting the learned embeddings in TSV or Pandas-supported format.
  * Interactive result inspector.
  * TSNE-based visualization, KPI summary visualization (mean rank, hit ratio) in various format. (csvs, figures, latex table)
  
The documentation is [here](https://pykg2vec.readthedocs.io/). 

## Repository Structure

* **pykg2vec/config**: This folder consists of the configuration module. It provides the necessary configuration to parse the datasets, and also consists of the baseline hyperparameters for the knowledge graph embedding algorithms. 
* **pykg2vec/core**: This folder consists of the core codes of the knowledge graph embedding algorithms. Inside this folder, each algorithm is implemented as a separate python module. 
* **pykg2vec/utils**: This folder consists of modules providing various utilities, such as data preparation, data visualization, and evaluation of the algorithms, data generators, baynesian optimizer.
* **pykg2vec/example**: This folder consists of example codes that can be used to run individual modules or run all the modules at once or tune the model.

![](https://github.com/Sujit-O/pykg2vec/blob/master/figures/pykg2vec_structure.png?raw=true)

## To Get Started 
Pykg2vec aims to minimize the dependency on other libraries as far as possible to rapidly test the algorithms against different datasets. In pykg2vec, we won't focus in run-time performance at this moment. **However, we do encourage users to install the tensorflow-gpu for speeding up the training! the guide to install Tensorflow can be found [here](https://www.tensorflow.org/install).** 
In the future, may provide faster implementation of each of the algorithms. (C++ implementations to come!)

Before using pykg2vec, we strongly recommend users to set up a virtual work environment (Venv or Anaconda) and to have the following packages installed:
* Python >= 3.6
* tensorflow==`<version suitable for your workspace>` or tensorflow-gpu=`<version suitable for your workspace>`

Three ways to install pykg2vec are described as follows.
```bash
#Install pykg2vec from PyPI:  
$ pip install pykg2vec

# (Suggested!) Install stable version directly from github repo:
$ git clone https://github.com/Sujit-O/pykg2vec.git
$ cd pykg2vec
$ python setup.py install

#Install development version directly from github repo:  
$ git clone https://github.com/Sujit-O/pykg2vec.git
$ cd pykg2vec
$ git checkout development
$ python setup.py install
```

## Usage Examples

### 1.Running a single algorithm: 
train.py
```python
from pykg2vec.utils.kgcontroller import KnowledgeGraph
from pykg2vec.config.config import Importer, KGEArgParser
from pykg2vec.utils.trainer import Trainer

def main():
    # getting the customized configurations from the command-line arguments.
    args = KGEArgParser().get_args()

    # Preparing data and cache the data for later usage
    knowledge_graph = KnowledgeGraph(dataset=args.dataset_name, negative_sample=args.sampling)
    knowledge_graph.prepare_data()

    # Extracting the corresponding model config and definition from Importer(). 
    config_def, model_def = Importer().import_model_config(args.model_name.lower())
    config = config_def(args=args)
    model = model_def(config)

    # Create, Compile and Train the model. While training, several evaluation will be performed.
    trainer = Trainer(model=model, debug=args.debug)
    trainer.build_model()
    trainer.train_model()


if __name__ == "__main__":
    main()
```

Pykg2vec aims to include most of the state-of-the-art KGE methods. You can check [Implemented Algorithms](https://pykg2vec.readthedocs.io/en/latest/algos.html) for more details. With train.py you can try KGE methods using the following commands: 
```bash
# check all tunnable parameters.
$ python train.py -h 

# Train TransE on FB15k benchmark dataset.
$ python train.py -mn TransE

# Train using different KGE methods.
$ python train.py -mn [TransE|TransD|TransH|TransG|TransM|TransR|Complex|
                       distmult|KG2E|NTN|Rescal|SLM|SME|HoLE]

# Train TransE model using different benchmark datasets.
$ python train.py -mn TransE -ds [fb15k|wn18|wn18_rr|yago3_10|fb15k_237|
                                  ks|nations|umls|dl50a]
```
Some models are still under development [Conv2D|ConvKB|ProjE|RotatE|TuckER], however, they can be executed without exceptions. 

To use your own dataset, these steps are required:
1. For triples, store all of them in a text-format with each line formatted as follows, 
```
head\trelation\ttail
```
2. For the text file, separate it into three files according to your reference give names as follows, 
```
[name]-train.txt, [name]-valid.txt, [name]-test.txt
```
3. For those three files, create a folder [path_storing_text_files] to include them.
4. Once finished, you then can use the custom dataset to train on a specific model using command:
```
$ python train.py -mn TransE -ds [name] -dsp [path_storing_text_files] 
```

### 2. Tuning a single algorithm:
tune_model.py
```python

from pykg2vec.config.hyperparams import KGETuneArgParser
from pykg2vec.utils.bayesian_optimizer import BaysOptimizer

def main():
    # getting the customized configurations from the command-line arguments.
    args = KGETuneArgParser().get_args()

    # initializing bayesian optimizer and prepare data.
    bays_opt = BaysOptimizer(args=args)

    # perform the golden hyperparameter tuning. 
    bays_opt.optimize()
    
if __name__ == "__main__":
    main()
``` 
with tune_model.py we then can train the existed model using command:
```bach
python tune_model.py -h # check all tunnable parameters.
python tune_model.py -mn TransE # Tune TransE model.
```

## 3. Perform Inference Tasks (advanced):
inference.py
```python
import sys, code

from pykg2vec.utils.kgcontroller import KnowledgeGraph
from pykg2vec.config.config import Importer, KGEArgParser
from pykg2vec.utils.trainer import Trainer

def main():
    # getting the customized configurations from the command-line arguments.
    args = KGEArgParser().get_args(sys.argv[1:])

    # Preparing data and cache the data for later usage
    knowledge_graph = KnowledgeGraph(dataset=args.dataset_name, negative_sample=args.sampling, custom_dataset_path=args.dataset_path)
    knowledge_graph.prepare_data()

    # Extracting the corresponding model config and definition from Importer().
    config_def, model_def = Importer().import_model_config(args.model_name.lower())
    config = config_def(args=args)
    model = model_def(config)

    # Create, Compile and Train the model. While training, several evaluation will be performed.
    trainer = Trainer(model=model, debug=args.debug)
    trainer.build_model()
    trainer.train_model()
    
    #can perform all the inference here after training the model
    trainer.enter_interactive_mode()
    
    code.interact(local=locals())

    trainer.exit_interactive_mode()

if __name__ == "__main__":
    main()

```
For inference task, you can use the following command: 
```
python inference.py -mn TransE # train a model on FK15K dataset and enter interactive CMD for manual inference tasks.
python inference.py -mn TransE -ld true # pykg2vec will look for the location of cached pretrained parameters in your local.

# Once interactive mode is reached, you can execute instruction manually like
# Example 1: trainer.infer_tails(1,10,topk=5) => give the list of top-5 predicted tails. 
# Example 2: trainer.infer_heads(10,20,topk=5) => give the list of top-5 predicted heads.
# Example 3: trainer.infer_rels(1,20,topk=5) => give the list of top-5 predicted relations.
```

# Common Installation Problems

* [SSL: CERTIFICATE_VERIFY_FAILED with urllib](https://stackoverflow.com/questions/49183801/ssl-certificate-verify-failed-with-urllib)

# Cite
  Please kindly cite the paper corresponding  to the library. 

   ```
   @article{yu2019pykg2vec,
  title={Pykg2vec: A Python Library for Knowledge Graph Embedding},
  author={Yu, Shih Yuan and Rokka Chhetri, Sujit and Canedo, Arquimedes and Goyal, Palash and Faruque, Mohammad Abdullah Al},
  journal={arXiv preprint arXiv:1906.04239},
  year={2019}
}
