#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
sys.path.append("../")
import tensorflow as tf
from core.KGMeta import ModelMeta


class ProjE_pointwise(ModelMeta):
    """
    ------------------Paper Title-----------------------------
    ---
    ------------------Paper Authors---------------------------
    ---
    ------------------Summary---------------------------------
    ---
    """
    def __init__(self, config, data_handler):
        self.config = config
        self.data_handler = data_handler
        self.model_name = 'ProjE_pointwise'

        self.def_inputs()
        self.def_parameters()
        self.def_loss()
        
    def def_inputs(self):
        num_total_ent = self.data_handler.tot_entity

        self.test_h = tf.placeholder(tf.int32, [None])
        self.test_t = tf.placeholder(tf.int32, [None])
        self.test_r = tf.placeholder(tf.int32, [None])

        self.hr_h = tf.placeholder(tf.int32, [None]) #[m]
        self.hr_r = tf.placeholder(tf.int32, [None]) #[m]
        self.hr_t = tf.placeholder(tf.float32, [None, num_total_ent]) #[m, tot_entity]

        self.tr_t = tf.placeholder(tf.int32, [None]) #[m]
        self.tr_r = tf.placeholder(tf.int32, [None]) #[m]
        self.tr_h = tf.placeholder(tf.float32, [None, num_total_ent]) #[m, tot_entity]
    
    def def_parameters(self):
        num_total_ent = self.data_handler.tot_entity
        num_total_rel = self.data_handler.tot_relation
        k = self.config.hidden_size

        with tf.name_scope("embedding"):
            self.ent_embeddings = tf.get_variable(name="ent_embedding", shape=[num_total_ent, k],
                                                  initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            
            self.rel_embeddings = tf.get_variable(name="rel_embedding", shape=[num_total_rel, k],
                                                  initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            
            self.bc1 = tf.get_variable(name="bc1", shape=[k], initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.De1 = tf.get_variable(name="De1", shape=[k], initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.Dr1 = tf.get_variable(name="Dr1", shape=[k], initializer=tf.contrib.layers.xavier_initializer(uniform=False))

            self.bc2 = tf.get_variable(name="bc2", shape=[k], initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.De2 = tf.get_variable(name="De2", shape=[k], initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.Dr2 = tf.get_variable(name="Dr2", shape=[k], initializer=tf.contrib.layers.xavier_initializer(uniform=False))

            self.parameter_list = [self.ent_embeddings, self.rel_embeddings, self.bc1, self.De1, self.Dr1, self.bc2, self.De2, self.Dr2]
            
    def def_loss(self):
        norm_ent_embeddings = tf.nn.l2_normalize(self.ent_embeddings, -1) #[tot_ent, k]
        norm_rel_embeddings = tf.nn.l2_normalize(self.rel_embeddings, -1) #[tot_rel, k]

        emb_hr_h = tf.nn.embedding_lookup(norm_ent_embeddings, self.hr_h) #[m, k]
        emb_hr_r = tf.nn.embedding_lookup(norm_rel_embeddings, self.hr_r) #[m, k]

        emb_tr_t = tf.nn.embedding_lookup(norm_ent_embeddings, self.tr_t) #[m, k]
        emb_tr_r = tf.nn.embedding_lookup(norm_rel_embeddings, self.tr_r) #[m, k]

        hrt_sigmoid = self.g(tf.nn.dropout(self.f1(emb_hr_h, emb_hr_r), 0.5), norm_ent_embeddings)

        hrt_loss_left = - tf.reduce_sum((tf.log(tf.clip_by_value(hrt_sigmoid, 1e-10, 1.0)) * tf.maximum(0., self.hr_t)))
        hrt_loss_right= - tf.reduce_sum((tf.log(tf.clip_by_value(1-hrt_sigmoid, 1e-10, 1.0)) * tf.maximum(0., tf.negative(self.hr_t))))

        hrt_loss = hrt_loss_left + hrt_loss_right

        trh_sigmoid = self.g(tf.nn.dropout(self.f2(emb_tr_t, emb_tr_r), 0.5), norm_ent_embeddings)

        trh_loss_left = - tf.reduce_sum((tf.log(tf.clip_by_value(trh_sigmoid, 1e-10, 1.0)) * tf.maximum(0., self.tr_h)))
        trh_loss_right= - tf.reduce_sum((tf.log(tf.clip_by_value(1-trh_sigmoid, 1e-10, 1.0)) * tf.maximum(0., tf.negative(self.tr_h))))

        trh_loss = trh_loss_left + trh_loss_right
        self.loss = hrt_loss + trh_loss

    def f1(self, h, r):
        return tf.tanh(h*self.De1 + r*self.Dr1 + self.bc1)
    def f2(self, t, r):
        return tf.tanh(t*self.De2 + r*self.Dr2 + self.bc2)
    def g(self, f, W):
        return tf.sigmoid(tf.matmul(f, tf.transpose(W)))

    def test_step(self):
        num_entity = self.data_handler.tot_entity

        norm_ent_embeddings = tf.nn.l2_normalize(self.ent_embeddings, -1) #[tot_ent, k]
        norm_rel_embeddings = tf.nn.l2_normalize(self.rel_embeddings, -1) #[tot_rel, k]

        h_vec = tf.nn.embedding_lookup(norm_ent_embeddings, self.test_h) #[1, k]
        r_vec = tf.nn.embedding_lookup(norm_rel_embeddings, self.test_r) #[1, k]
        t_vec = tf.nn.embedding_lookup(norm_ent_embeddings, self.test_t) #[1, k]
        
        hrt_sigmoid = - self.g(self.f1(h_vec, r_vec), norm_ent_embeddings)
        trh_sigmoid = - self.g(self.f2(t_vec, r_vec), norm_ent_embeddings)
        
        _, self.head_rank      = tf.nn.top_k(trh_sigmoid, k=num_entity)
        _, self.tail_rank      = tf.nn.top_k(hrt_sigmoid, k=num_entity)

        return self.head_rank, self.tail_rank

    def embed(self, h, r, t):
        """function to get the embedding value"""
        emb_h = tf.nn.embedding_lookup(self.ent_embeddings, h)
        emb_r = tf.nn.embedding_lookup(self.rel_embeddings, r)
        emb_t = tf.nn.embedding_lookup(self.ent_embeddings, t)
        emb_h = tf.nn.l2_normalize(emb_h, axis=-1)
        emb_r = tf.nn.l2_normalize(emb_r, axis=-1)
        emb_t = tf.nn.l2_normalize(emb_t, axis=-1)
        
        proj_vec = self.get_proj(r)

        return self.projection(emb_h, proj_vec), emb_r, self.projection(emb_t, proj_vec)

    def get_embed(self, h, r, t, sess):
        """function to get the embedding value in numpy"""
        emb_h, emb_r, emb_t = self.embed(h, r, t)
        h, r, t = sess.run([emb_h, emb_r, emb_t])
        return h, r, t

    def get_proj_embed(self, h, r, t, sess):
        """function to get the projectd embedding value in numpy"""
        return self.get_embed(h, r, t, sess)