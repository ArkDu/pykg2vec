#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

sys.path.append("../")
import tensorflow as tf
from core.KGMeta import ModelMeta


class Complex(ModelMeta):
    """
    ------------------Paper Title-----------------------------
    ------------------Paper Authors---------------------------
    ------------------Summary---------------------------------
    """

    def __init__(self, config=None, data_stats=None):
        self.config = config
        self.data_stats = data_stats
        self.tot_ent = self.data_stats.tot_entity
        self.tot_rel = self.data_stats.tot_relation
        self.model_name = 'Ccmplex'

        self.def_inputs()
        self.def_parameters()
        self.def_layer()
        self.def_loss()

    def def_inputs(self):
        self.e1 = tf.placeholder(tf.int32, [None])
        self.r = tf.placeholder(tf.int32, [None])
        self.e2_multi1 = tf.placeholder(tf.float32, [None, self.data_stats.tot_entity])

        self.test_e1 = tf.placeholder(tf.int32, [None])
        self.test_e2 = tf.placeholder(tf.int32, [None])
        self.test_r = tf.placeholder(tf.int32, [None])
        self.test_r_rev = tf.placeholder(tf.int32, [None])
        self.test_e2_multi1 = tf.placeholder(tf.float32, [None, self.data_stats.tot_entity])
        self.test_e2_multi2 = tf.placeholder(tf.float32, [None, self.data_stats.tot_entity])

    def def_parameters(self):
        k = self.config.hidden_size
        with tf.name_scope("embedding"):
            self.emb_e_real = tf.get_variable(name="emb_e_real", shape=[self.tot_ent, k],
                                              initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.emb_e_img = tf.get_variable(name="emb_e_img", shape=[self.tot_ent, k],
                                             initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.emb_rel_real = tf.get_variable(name="emb_rel_real", shape=[self.tot_rel, k],
                                                initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.emb_rel_img = tf.get_variable(name="emb_rel_img", shape=[self.tot_rel, k],
                                               initializer=tf.contrib.layers.xavier_initializer(uniform=False))

        self.parameter_list = [self.emb_e_real, self.emb_e_img, self.emb_rel_real, self.emb_rel_img]

    def def_loss(self):
        # norm_emb_e_real = tf.nn.l2_normalize(self.emb_e_real, axis=1)
        # norm_emb_e_img = tf.nn.l2_normalize(self.emb_e_img, axis=1)
        # norm_emb_rel_real = tf.nn.l2_normalize(self.emb_rel_real, axis=1)
        # norm_emb_rel_img = tf.nn.l2_normalize(self.emb_rel_img, axis=1)

        e1_embedded_real = tf.nn.embedding_lookup(self.emb_e_real, self.e1)
        rel_embedded_real = tf.nn.embedding_lookup(self.emb_rel_real, self.r)
        e1_embedded_img = tf.nn.embedding_lookup(self.emb_e_img, self.e1)
        rel_embedded_img = tf.nn.embedding_lookup(self.emb_rel_img, self.r)

        e1_embedded_real,rel_embedded_real = self.layer(e1_embedded_real,rel_embedded_real)
        e1_embedded_img, rel_embedded_img = self.layer(e1_embedded_img, rel_embedded_img)

        realrealreal = tf.matmul(e1_embedded_real * rel_embedded_real, tf.transpose(self.emb_e_real))
        realimgimg = tf.matmul(e1_embedded_real * rel_embedded_img, tf.transpose(self.emb_e_img))
        imgrealimg = tf.matmul(e1_embedded_img * rel_embedded_real, tf.transpose(self.emb_e_img))
        imgimgreal = tf.matmul(e1_embedded_img * rel_embedded_img, tf.transpose(self.emb_e_real))

        pred = realrealreal + realimgimg + imgrealimg - imgimgreal
        pred = tf.nn.sigmoid(pred)

        e2_multi1 = self.e2_multi1 * (1.0 - self.config.label_smoothing) + 1.0 / self.data_handler.tot_entity
        e2_multi1 = tf.reshape(e2_multi1, [self.config.batch_size, self.data_stats])

        self.loss = tf.reduce_mean(tf.keras.backend.binary_crossentropy(e2_multi1, pred))

    def def_layer(self):
        self.inp_drop = tf.keras.layers.Dropout(rate=self.config.input_dropout)

    def layer(self, e1, rel):
        e1 = tf.squeeze(e1)
        rel = tf.squeeze(rel)
        e1 = self.inp_drop(e1)
        rel = self.inp_drop(rel)
        return e1, rel

    def test_step(self):
        ent_emb_norm = tf.nn.l2_normalize(self.ent_embeddings, axis=1)
        rel_emb_norm = tf.nn.l2_normalize(self.rel_embeddings, axis=1)

        e1 = tf.nn.embedding_lookup(ent_emb_norm, self.test_e1)
        e2 = tf.nn.embedding_lookup(ent_emb_norm, self.test_e2)

        r = tf.nn.embedding_lookup(rel_emb_norm, self.test_r)
        r_rev = tf.nn.embedding_lookup(rel_emb_norm, self.test_r_rev)

        stacked_head_e = tf.reshape(e1, [-1, 10, 20, 1])
        stacked_head_r = tf.reshape(r, [-1, 10, 20, 1])

        stacked_tail_e = tf.reshape(e2, [-1, 10, 20, 1])
        stacked_tail_r = tf.reshape(r_rev, [-1, 10, 20, 1])

        stacked_hr = tf.concat([stacked_head_e, stacked_head_r], 1)
        stacked_tr = tf.concat([stacked_tail_e, stacked_tail_r], 1)

        e2_multi1 = tf.scalar_mul((1.0 - self.config.label_smoothing),
                                  self.test_e2_multi1) + (1.0 / self.data_handler.tot_entity)
        e2_multi2 = tf.scalar_mul((1.0 - self.config.label_smoothing),
                                  self.test_e2_multi2) + (1.0 / self.data_handler.tot_entity)

        pred4head = self.layer(stacked_hr)
        pred4tail = self.layer(stacked_tr)

        head_vec = tf.keras.backend.binary_crossentropy(e2_multi1, pred4head)
        tail_vec = tf.keras.backend.binary_crossentropy(e2_multi2, pred4tail)

        _, head_rank = tf.nn.top_k(tf.math.negative(head_vec), k=self.data_handler.tot_entity)
        _, tail_rank = tf.nn.top_k(tf.math.negative(tail_vec), k=self.data_handler.tot_entity)

        return head_rank, tail_rank

    def embed(self, h, r, t):
        """function to get the embedding value"""
        emb_h = tf.nn.embedding_lookup(self.ent_embeddings, h)
        emb_r = tf.nn.embedding_lookup(self.rel_embeddings, r)
        emb_t = tf.nn.embedding_lookup(self.ent_embeddings, t)
        return emb_h, emb_r, emb_t

    def get_embed(self, h, r, t, sess=None):
        """function to get the embedding value in numpy"""
        emb_h, emb_r, emb_t = self.embed(h, r, t)
        h, r, t = sess.run([emb_h, emb_r, emb_t])
        return h, r, t

    def get_proj_embed(self, h, r, t, sess):
        """function to get the projected embedding value in numpy"""
        return self.get_embed(h, r, t, sess)


if __name__ == '__main__':
    # Unit Test Script with tensorflow Eager Execution
    import tensorflow as tf

    tf.enable_eager_execution()
    batch = 128
    embed_dim = 100
    tot_entity = 147000
    train = True
    pos_h_e = tf.random_normal([batch // 2, embed_dim])
    print('pos_r_e:', pos_h_e)
    pos_r_e = tf.random_normal([batch // 2, embed_dim])
    print('pos_r_e:', pos_r_e)
    pos_t_e = tf.random_normal([batch // 2, embed_dim])
    print('pos_t_e:', pos_t_e)
    neg_h_e = tf.random_normal([batch // 2, embed_dim])
    print('neg_h_e:', neg_h_e)
    neg_r_e = tf.random_normal([batch // 2, embed_dim])
    print('neg_r_e:', neg_r_e)
    neg_t_e = tf.random_normal([batch // 2, embed_dim])
    print('neg_t_e:', neg_t_e)
    stacked_inputs_e = tf.concat([pos_h_e, neg_h_e], 0)
    stacked_inputs_r = tf.concat([pos_r_e, neg_r_e], 0)
    stacked_inputs_e = tf.reshape(stacked_inputs_e, [batch, 10, -1, 1])
    stacked_inputs_r = tf.reshape(stacked_inputs_r, [batch, 10, -1, 1])
    stacked_inputs = tf.concat([stacked_inputs_e, stacked_inputs_r], 1)
    stacked_inputs_t = tf.concat([pos_t_e, neg_t_e], 0)
    print('stacked_inputs:', stacked_inputs)
    x = tf.layers.batch_normalization(stacked_inputs, axis=0)
    print("x_batch normalize:", x)
    x = tf.layers.dropout(x, rate=0.2)
    print("x_dropped out:", x)
    x = tf.layers.conv2d(x, 32, [3, 3], strides=(1, 1), padding='valid', activation=None)
    print("x_conv2d:", x)
    x = tf.layers.batch_normalization(x, axis=1)
    print("x_batch normalize:", x)
    x = tf.nn.relu(x)
    print("x_relu activation:", x)
    x = tf.layers.dropout(x, rate=0.2)
    print("x_dropped out:", x)
    x = tf.reshape(x, [batch, -1])
    print("x_reshaped:", x)
    x = tf.layers.dense(x, units=embed_dim)
    print("x_dense:", x)
    x = tf.layers.dropout(x, rate=0.3)
    print("x_droppedout:", x)
    x = tf.layers.batch_normalization(x, axis=1)
    print("x_batch normalize:", x)
    x = tf.nn.relu(x)
    print("x_relu activation:", x)
    W = tf.get_variable(name="ent_embedding", shape=[embed_dim, embed_dim],
                        initializer=tf.contrib.layers.xavier_initializer(uniform=False))
    print("ent_embedding:", W)
    x = tf.matmul(x, tf.transpose(W))
    print("x_mul with ent_embeeding:", x)
    b = tf.get_variable(name="b", shape=[batch, tot_entity],
                        initializer=tf.contrib.layers.xavier_initializer(uniform=False))
    print("bias:", b)
    x = tf.add(x, b)
    print("x_added with bias:", x)
    ent_embeddings = tf.get_variable(name="ent_embedding", shape=[tot_entity, embed_dim],
                                     initializer=tf.contrib.layers.xavier_initializer(uniform=False))
    if train:
        x = tf.reduce_sum(tf.matmul(x, tf.transpose(stacked_inputs_t)), 1)
    else:
        x = tf.reduce_sum(tf.matmul(x, tf.transpose(ent_embeddings)), 1)
    pred = tf.nn.sigmoid(x)
    print("prediction:", pred)

    import tensorflow as tf

    tf.enable_eager_execution()
    batch = 128
    embed_dim = 100
    tot_entity = 147000
    train = False
    input_dropout = 0.2
    input_dropout = 0.2
    hidden_dropout = 0.3
    feature_map_dropout = 0.2
    ent_embeddings = tf.get_variable(name="ent_embedding", shape=[tot_entity, embed_dim],
                                     initializer=tf.contrib.layers.xavier_initializer(uniform=False))
    W = tf.get_variable(name="ent_embedding", shape=[embed_dim, embed_dim],
                        initializer=tf.contrib.layers.xavier_initializer(uniform=False))
    b = tf.get_variable(name="b", shape=[batch, embed_dim],
                        initializer=tf.contrib.layers.xavier_initializer(uniform=False))
    print("ent_embedding:", W)
    pos_h_e = tf.random_normal([1, embed_dim])
    print('pos_r_e:', pos_h_e)
    pos_r_e = tf.random_normal([1, embed_dim])
    print('pos_r_e:', pos_r_e)
    pos_t_e = tf.random_normal([1, embed_dim])
    stacked_inputs_h = tf.reshape(pos_h_e, [1, 10, -1, 1])
    stacked_inputs_r = tf.reshape(pos_r_e, [1, 10, -1, 1])
    stacked_inputs_hr = tf.concat([stacked_inputs_h, stacked_inputs_r], 1)
    x = tf.layers.batch_normalization(stacked_inputs_hr, axis=0)
    x = tf.layers.dropout(x, rate=input_dropout)
    x = tf.layers.conv2d(x, 32, [3, 3], strides=(1, 1), padding='valid', activation=None)
    x = tf.layers.batch_normalization(x, axis=1)
    x = tf.nn.relu(x)
    x = tf.layers.dropout(x, rate=feature_map_dropout)
    if train:
        x = tf.reshape(x, [batch_size, -1])
    else:
        x = tf.reshape(x, [1, -1])

    x = tf.layers.dense(x, units=embed_dim)
    x = tf.layers.dropout(x, rate=hidden_dropout)
    x = tf.layers.batch_normalization(x, axis=1)
    x = tf.nn.relu(x)
    x = tf.matmul(x, W)
    if train:
        x = tf.add(x, b)
    else:
        x = tf.add(x, tf.slice(b, [0, 0], [1, embed_dim]))

    if train:
        x = tf.reduce_sum(tf.matmul(x, tf.transpose(st_inp_t)), 1)
        x = tf.reduce_sum(tf.matmul(x, tf.transpose(ent_emb_norm)), 1)
    else:
        ent_emb_norm = tf.nn.l2_normalize(ent_embeddings, axis=1)
        x = tf.matmul(x, tf.transpose(ent_emb_norm))
    pred = tf.nn.sigmoid(x)
