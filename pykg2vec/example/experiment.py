'''
=========================
Train multiple Algorithm
=========================
In this example, we will show how to import all the modules to start training and algorithm
'''
# Author: Sujit Rokka Chhetri and Shiy Yuan Yu
# License: MIT


from pykg2vec.utils.kgcontroller import KnowledgeGraph
from pykg2vec.config.config import Importer, KGEArgParser
from pykg2vec.utils.trainer import Trainer


def experiment(model_name):
    args = KGEArgParser().get_args([])
    args.exp = True
    args.dataset_name = "fb15k"

    # Preparing data and cache the data for later usage
    knowledge_graph = KnowledgeGraph(dataset=args.dataset_name, negative_sample=args.sampling, custom_dataset_path=args.dataset_path)
    knowledge_graph.prepare_data()

    # Extracting the corresponding model config and definition from Importer().
    config_def, model_def = Importer().import_model_config(model_name)
    config = config_def(args=args)
    model = model_def(config)

    # Create, Compile and Train the model. While training, several evaluation will be performed.
    trainer = Trainer(model=model)
    trainer.build_model()
    trainer.train_model()

if __name__ == "__main__":

    # examples of train an algorithm on a benchmark dataset.
    experiment("transe", "fb15k")
    experiment("transh", "fb15k")
    experiment("transr", "fb15k")

    # other combination we are still working on them. 
    # experiment("transe", "wn18_rr")