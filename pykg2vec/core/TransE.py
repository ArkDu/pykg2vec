#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from pykg2vec.core.KGMeta import ModelMeta, InferenceMeta


class TransE(ModelMeta):
    """ `Translating Embeddings for Modeling Multi-relational Data`_

        TransE is an energy based model which represents the
        relationships as translations in the embedding space. Which
        means that if (h,l,t) holds then the embedding of the tail
        't' should be close to the embedding of head entity 'h'
        plus some vector that depends on the relationship 'l'.
        Both entities and relations are vectors in the same space.

        Args:
            config (object): Model configuration parameters.

        Attributes:
            config (object): Model configuration.
            model_name (str): Name of the model.

        Examples:
            >>> from pykg2vec.core.TransE import TransE
            >>> from pykg2vec.utils.trainer import Trainer
            >>> model = TransE()
            >>> trainer = Trainer(model=model, debug=False)
            >>> trainer.build_model()
            >>> trainer.train_model()

        Portion of the code based on `OpenKE_TransE`_ and `wencolani`_.

        .. _OpenKE_TransE: https://github.com/thunlp/OpenKE/blob/master/models/TransE.py

        .. _wencolani: https://github.com/wencolani/TransE.git

        .. _Translating Embeddings for Modeling Multi-relational Data:
            http://papers.nips.cc/paper/5071-translating-embeddings-for-modeling-multi-rela
    """

    def __init__(self, config=None):
        super(TransE, self).__init__()
        self.config = config
        self.model_name = 'TransE'

    def def_parameters(self):
        """Defines the model parameters.

           Attributes:
               num_total_ent (int): Total number of entities.
               num_total_rel (int): Total number of relations.
               k (Tensor): Size of the latent dimesnion for entities and relations.
               ent_embeddings (Tensor Variable): Lookup variable containing  embedding of the entities.
               rel_embeddings  (Tensor Variable): Lookup variable containing  embedding of the relations.
               parameter_list  (list): List of Tensor parameters.
        """
        num_total_ent = self.config.kg_meta.tot_entity
        num_total_rel = self.config.kg_meta.tot_relation
        k = self.config.hidden_size
        
        emb_initializer = tf.initializers.glorot_normal()

        self.ent_embeddings = tf.Variable(emb_initializer(shape=(num_total_ent, k)), name="ent_embedding")
        self.rel_embeddings = tf.Variable(emb_initializer(shape=(num_total_rel, k)), name="rel_embedding")
        self.parameter_list = [self.ent_embeddings, self.rel_embeddings]

    def dissimilarity(self, h, r, t, axis=-1):
        """Function to calculate distance measure in embedding space.
        
        if used in def_loss,
            h, r, t shape [b, k], return shape will be [b]
        if used in test_batch, 
            h, r, t shape [1, tot_ent, k] or [b, 1, k], return shape will be [b, tot_ent]

        Args:
            h (Tensor): shape [b, k] Head entities in a batch. 
            r (Tensor): shape [b, k] Relation entities in a batch.
            t (Tensor): shape [b, k] Tail entities in a batch.
            axis (int): Determines the axis for reduction

        Returns:
            Tensor: shape [b] the aggregated distance measure.
        """
        norm_h = tf.nn.l2_normalize(h, axis=axis)
        norm_r = tf.nn.l2_normalize(r, axis=axis)
        norm_t = tf.nn.l2_normalize(t, axis=axis)
        
        dissimilarity = norm_h + norm_r - norm_t 

        if self.config.L1_flag:
            dissimilarity = tf.math.abs(dissimilarity) # L1 norm 
        else:
            dissimilarity = tf.math.square(dissimilarity) # L2 norm
        
        return tf.reduce_sum(dissimilarity, axis=axis)

    def get_loss(self, pos_h, pos_r, pos_t, neg_h, neg_r, neg_t):
        """Defines the loss function for the algorithm."""
        pos_h_e, pos_r_e, pos_t_e = self.embed(pos_h, pos_r, pos_t)
        pos_score = self.dissimilarity(pos_h_e, pos_r_e, pos_t_e)

        neg_h_e, neg_r_e, neg_t_e = self.embed(neg_h, neg_r, neg_t)      
        neg_score = self.dissimilarity(neg_h_e, neg_r_e, neg_t_e)

        loss = self.pairwise_margin_loss(pos_score, neg_score)

        return loss

    def predict(self, h, r, t, topk=-1):
        """Function that performs prediction for TransE. 
           shape of h can be either [num_tot_entity] or [1]. 
           shape of t can be either [num_tot_entity] or [1].

          Returns:
              Tensors: Returns ranks of head and tail.
        """
        h_e, r_e, t_e = self.embed(h, r, t)

        score_head = self.dissimilarity(h_e, r_e, t_e)
        
        _, rank = tf.nn.top_k(score_head, k=topk)

        return rank
    
    def test_batch(self, h_batch, r_batch, t_batch):
        """Function that performs batch testing for the algorithm.

          Returns:
              Tensors: Returns ranks of head and tail.
        """
        h_e, r_e, t_e = self.embed(h_batch, r_batch, t_batch)

        expanded_ent_embeddings = tf.expand_dims(self.ent_embeddings, axis=0)
        score_head = self.dissimilarity(expanded_ent_embeddings,
                                        tf.expand_dims(r_e, axis=1),
                                        tf.expand_dims(t_e, axis=1))
        score_tail = self.dissimilarity(tf.expand_dims(h_e, axis=1),
                                        tf.expand_dims(r_e, axis=1),
                                        expanded_ent_embeddings)

        _, head_rank = tf.nn.top_k(score_head, k=self.config.kg_meta.tot_entity)
        _, tail_rank = tf.nn.top_k(score_tail, k=self.config.kg_meta.tot_entity)

        return head_rank, tail_rank

    def infer_tails(self, h, r, topk):
        """Function to infer top k tails for given head and relation.

        Args:
            h (int): Head entities ids.
            r (int): Relation ids of the triple.
            topk (int): Top K values to infer.

        Returns:
            Tensors: Returns the list of tails tensor.
        """
        norm_ent_embeddings = tf.nn.l2_normalize(self.ent_embeddings, axis=1)
        norm_rel_embeddings = tf.nn.l2_normalize(self.rel_embeddings, axis=1)

        head_vec = tf.nn.embedding_lookup(norm_ent_embeddings, h)
        rel_vec = tf.nn.embedding_lookup(norm_rel_embeddings, r)

        score_tail = self.dissimilarity(head_vec, rel_vec, norm_ent_embeddings)
        _, tails = tf.nn.top_k(-score_tail, k=topk)

        return tails

    def infer_heads(self, r, t, topk):
        """Function to infer top k head for given relation and tail.

        Args:
            t (int): tail entities ids.
            r (int): Relation ids of the triple.
            topk (int): Top K values to infer.

        Returns:
            Tensors: Returns the list of heads tensor.
        """
        norm_ent_embeddings = tf.nn.l2_normalize(self.ent_embeddings, axis=1)
        norm_rel_embeddings = tf.nn.l2_normalize(self.rel_embeddings, axis=1)

        tail_vec = tf.nn.embedding_lookup(norm_ent_embeddings, t)
        rel_vec = tf.nn.embedding_lookup(norm_rel_embeddings, r)

        score_head = self.dissimilarity(norm_ent_embeddings, rel_vec, tail_vec)
        _, heads = tf.nn.top_k(-score_head, k=topk)

        return heads

    def infer_rels(self, h, t, topk):
        """Function to infer top k relations for given head and tail.

        Args:
            h (int): Head entities ids.
            t (int): Tail entities ids.
            topk (int): Top K values to infer.

        Returns:
            Tensors: Returns the list of rels tensor.
        """
        norm_ent_embeddings = tf.nn.l2_normalize(self.ent_embeddings, axis=1)
        norm_rel_embeddings = tf.nn.l2_normalize(self.rel_embeddings, axis=1)

        head_vec = tf.nn.embedding_lookup(norm_ent_embeddings, h)
        tail_vec = tf.nn.embedding_lookup(norm_ent_embeddings, t)

        score_rel = self.dissimilarity(head_vec, norm_rel_embeddings, tail_vec)
        _, rels = tf.nn.top_k(-score_rel, k=topk)

        return rels

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

    def get_embed(self, h, r, t, sess):
        """Function to get the embedding value in numpy.

           Args:
               h (Tensor): Head entities ids.
               r (Tensor): Relation ids of the triple.
               t (Tensor): Tail entity ids of the triple.
               sess (object): Tensorflow Session object.

            Returns:
                Tensors: Returns head, relation and tail embedding Tensors.
        """
        emb_h, emb_r, emb_t = self.embed(h, r, t)
        h, r, t = sess.run([emb_h, emb_r, emb_t])
        return h, r, t

    def get_proj_embed(self, h, r, t, sess=None):
        """"Function to get the projected embedding value in numpy.

           Args:
               h (Tensor): Head entities ids.
               r (Tensor): Relation ids of the triple.
               t (Tensor): Tail entity ids of the triple.
               sess (object): Tensorflow Session object.

            Returns:
                Tensors: Returns head, relation and tail embedding Tensors.
         """
        return self.get_embed(h, r, t, sess)
