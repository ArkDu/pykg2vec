#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module is for testing unit functions of training
"""
import pytest

from pykg2vec.config.config import KGEArgParser, Importer
from pykg2vec.utils.trainer import Trainer, Monitor
from pykg2vec.utils.kgcontroller import KnowledgeGraph
import tensorflow as tf
tf.config.experimental_run_functions_eagerly(True)


@pytest.mark.skip(reason="This is a functional method.")
def get_model(result_path_dir, configured_epochs, patience, early_stop_epoch, config_key):
    args = KGEArgParser().get_args([])

    knowledge_graph = KnowledgeGraph(dataset="Freebase15k")
    knowledge_graph.prepare_data()

    config_def, model_def = Importer().import_model_config(config_key)
    config = config_def(args=args)

    config.epochs = configured_epochs
    config.test_step = 1
    config.test_num = 1
    config.disp_result = False
    config.save_model = False
    config.path_result = result_path_dir
    config.early_stop_epoch = early_stop_epoch
    config.debug = True
    config.patience = patience

    return model_def(config)

@pytest.mark.parametrize("config_key",
                         filter(lambda x: x != "conve" and x != "convkb" and x != "transg", list(Importer().configMap.keys())))
def test_full_epochs(tmpdir, config_key):
    result_path_dir = tmpdir.mkdir("result_path")
    configured_epochs = 10
    model = get_model(result_path_dir, configured_epochs, -1, 5, config_key)

    trainer = Trainer(model=model)
    trainer.build_model()
    actual_epochs = trainer.train_model()

    assert actual_epochs == configured_epochs - 1

def test_early_stopping_on_loss(tmpdir):
    result_path_dir = tmpdir.mkdir("result_path")
    configured_epochs = 10
    model = get_model(result_path_dir, configured_epochs, 1, 1, "complex")

    trainer = Trainer(model=model)
    trainer.build_model()
    actual_epochs = trainer.train_model()

    assert actual_epochs < configured_epochs - 1

@pytest.mark.parametrize("monitor", [
    Monitor.MEAN_RANK,
    Monitor.FILTERED_MEAN_RANK,
    Monitor.MEAN_RECIPROCAL_RANK,
    Monitor.FILTERED_MEAN_RECIPROCAL_RANK,
    Monitor.HIT1,
    Monitor.FILTERED_HIT1,
    Monitor.HIT3,
    Monitor.FILTERED_HIT3,
    Monitor.HIT5,
    Monitor.FILTERED_HIT5,
    Monitor.HIT10,
    Monitor.FILTERED_HIT10
])
def test_early_stopping_on_ranks(tmpdir, monitor):
    result_path_dir = tmpdir.mkdir("result_path")
    configured_epochs = 10
    model = get_model(result_path_dir, configured_epochs, 0, 1, "complex")

    trainer = Trainer(model=model)
    trainer.build_model()
    actual_epochs = trainer.train_model(monitor=monitor)

    assert actual_epochs < configured_epochs - 1

def test_throw_exception_on_unknown_monitor(tmpdir):
    result_path_dir = tmpdir.mkdir("result_path")
    configured_epochs = 10
    model = get_model(result_path_dir, configured_epochs, 0, 1, "complex")

    trainer = Trainer(model=model)
    trainer.build_model()

    with pytest.raises(NotImplementedError, match="Unknown monitor dummy"):
        trainer.train_model(monitor="dummy")
