#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module is for testing unit functions of tuning model
"""
import pytest

from unittest.mock import patch
from pykg2vec.data.kgcontroller import KnowledgeGraph
from pykg2vec.common import KGETuneArgParser
from pykg2vec.utils.bayesian_optimizer import BaysOptimizer


@pytest.mark.skip(reason="This is a functional method.")
def tunning_function(name):
    """Function to test the tuning of the models."""
    knowledge_graph = KnowledgeGraph(dataset="freebase15k")
    knowledge_graph.prepare_data()

    # getting the customized configurations from the command-line arguments.
    args = KGETuneArgParser().get_args([])

    # initializing bayesian optimizer and prepare data.
    args.debug = True
    args.model = name

    bays_opt = BaysOptimizer(args=args)
    bays_opt.config_local.test_num = 10

    # perform the golden hyperparameter tuning. 
    bays_opt.optimize()

    assert bays_opt.return_best() is not None

@pytest.mark.parametrize('model_name', [
    'analogy',
    'complex',
    'complexn3',
    'cp',
    'distmult',
    'hole',
    'kg2e',
    'ntn',
    'rescal',
    'rotate',
    'simple',
    'simple_ignr',
    'slm',
    'sme',
    'sme_bl',
    'transe',
    'transh',
    'transm',
    'transd',
    'transr',
])
def test_tuning(model_name):
    """Function to test the tuning function."""
    tunning_function(model_name)

@patch('pykg2vec.utils.bayesian_optimizer.fmin')
def test_return_empty_before_optimization(mocked_fmin):
    """Function to test the tuning of the models."""
    knowledge_graph = KnowledgeGraph(dataset="freebase15k")
    knowledge_graph.prepare_data()

    # getting the customized configurations from the command-line arguments.
    args = KGETuneArgParser().get_args([])

    # initializing bayesian optimizer and prepare data.
    args.debug = True
    args.model = 'analogy'

    bays_opt = BaysOptimizer(args=args)
    bays_opt.config_local.test_num = 10

    with pytest.raises(Exception) as e:
        bays_opt.return_best()

    assert mocked_fmin.called is False
    assert e.value.args[0] == 'Cannot find golden setting. Has optimize() been called?'
