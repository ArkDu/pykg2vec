#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from pykg2vec.core.KGMeta import ModelMeta
from pykg2vec.utils.generator import TrainingStrategy

class HoLE(ModelMeta):
    """`Holographic Embeddings of Knowledge Graphs`_.

    HoLE employs the circular correlation to create composition correlations. It
    is able to represent and capture the interactions betweek entities and relations
    while being efficient to compute, easier to train and scalable to large dataset.

    Args:
        config (object): Model configuration parameters.

    Attributes:
        config (object): Model configuration.
        model_name (str): Name of the model.
    
    Examples:
        >>> from pykg2vec.core.HoLE import HoLE
        >>> from pykg2vec.utils.trainer import Trainer
        >>> model = HoLE()
        >>> trainer = Trainer(model=model)
        >>> trainer.build_model()
        >>> trainer.train_model()

    .. _Holographic Embeddings of Knowledge Graphs:
        https://arxiv.org/pdf/1510.04935.pdf

    """

    def __init__(self, config):
        super(HoLE, self).__init__()
        self.config = config
        self.model_name = 'HoLE'
        self.training_strategy = TrainingStrategy.PAIRWISE_BASED
        
    def def_parameters(self):
        """Defines the model parameters.
           
           Attributes:
               num_total_ent (int): Total number of entities. 
               num_total_rel (int): Total number of relations. 
               k (Tensor): Size of the latent dimesnion for entities and relations.
               ent_embeddings  (Tensor Variable): Lookup variable containing embedding of the entities.
               rel_embeddings  (Tensor Variable): Lookup variable containing embedding of the relations.
               b  (Tensor Variable): Variable storing the bias values.
               parameter_list  (list): List of Tensor parameters.
        """ 
        num_total_ent = self.config.kg_meta.tot_entity
        num_total_rel = self.config.kg_meta.tot_relation
        initializer = tf.initializers.glorot_normal()

        self.ent_embeddings = tf.Variable(initializer(shape=(num_total_ent, self.config.hidden_size)), name="ent_embedding")
        self.rel_embeddings = tf.Variable(initializer(shape=(num_total_rel, self.config.hidden_size)), name="rel_embedding")
        self.parameter_list = [self.ent_embeddings, self.rel_embeddings]

    def forward(self, h, r, t):
        h_e, r_e, t_e = self.embed(h, r, t)
        r_e = tf.nn.l2_normalize(r_e, -1)
        h_e = tf.cast(h_e, tf.complex64)
        t_e = tf.cast(t_e, tf.complex64)
        e = tf.math.real(tf.signal.ifft(tf.math.conj(tf.signal.fft(h_e)) * tf.signal.fft(t_e)))
        return -tf.sigmoid(tf.reduce_sum(r_e * e, 1))

    def embed(self, h, r, t):
        """Function to get the embedding value.
           
           Args:
               h (Tensor): Head entities ids.
               r (Tensor): Relation ids of the triple.
               t (Tensor): Tail entity ids of the triple.

            Returns:
                Tensors: Returns head, relation and tail embedding Tensors.
        """
        emb_h = tf.nn.embedding_lookup(self.ent_embeddings, h)
        emb_r = tf.nn.embedding_lookup(self.rel_embeddings, r)
        emb_t = tf.nn.embedding_lookup(self.ent_embeddings, t)
        return emb_h, emb_r, emb_t