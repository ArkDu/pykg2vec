#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from pykg2vec.core.KGMeta import ModelMeta


class ConvKB(ModelMeta):
    """`A Novel Embedding Model for Knowledge Base Completion Based on Convolutional Neural Network`_

    ConvKB, each triple (head entity, relation, tail entity) is represented as a 3-
    column matrix where each column vector represents a triple element

    Args:
        config (object): Model configuration parameters.
    
    Attributes:
        config (object): Model configuration.
        data_stats (object): ModelMeta object instance. It consists of the knowledge graph metadata.
        model (str): Name of the model.
        last_dim (int): The size of the last dimesion, depends on hidden size.

    
    Examples:
        >>> from pykg2vec.core.ConvKB import ConvKB
        >>> from pykg2vec.utils.trainer import Trainer
        >>> model = ConvKB()
        >>> trainer = Trainer(model=model, debug=False)
        >>> trainer.build_model()
        >>> trainer.train_model()
    
    Portion of the code based on Niubohan_ and BookmanHan_.
    .. _daiquocnguyen:
        https://github.com/daiquocnguyen/ConvKB

    .. _A Novel Embedding Model for Knowledge Base Completion Based on Convolutional Neural Network:
        https://www.aclweb.org/anthology/N18-2053

    """

    def __init__(self, config=None):
        super(ConvKB, self).__init__()
        self.config = config
        self.model_name = 'ConvKB'

        # raise NotImplementedError("TransG is yet finished in pykg2vec.")
        self.def_layer()
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
        k = self.config.hidden_size

        emb_initializer = tf.initializers.glorot_normal()
        self.ent_embeddings = tf.Variable(emb_initializer(shape=(num_total_ent, k)), name="ent_embedding")
        self.rel_embeddings = tf.Variable(emb_initializer(shape=(num_total_rel, k)), name="rel_embedding")
        self.parameter_list = [self.ent_embeddings, self.rel_embeddings]

    def def_layer(self):
        """Defines the layers of the algorithm."""
        self.conv_list = [tf.keras.layers.Conv2D(self.config.num_filters, 
            (self.config.sequence_length, filter_size), 
            padding = 'valid', 
            use_bias= True, 
            data_format="channels_first",
            strides = (1,1),
            activation = tf.keras.layers.ReLU()) for filter_size in self.config.filter_sizes]
        self.drop = tf.keras.layers.Dropout(rate=self.config.hidden_dropout)
        self.fc1 = tf.keras.layers.Dense(1,
            use_bias=True,
            kernel_regularizer = tf.keras.regularizers.l2(l=self.config.lmbda),
            bias_regularizer = tf.keras.regularizers.l2(l=self.config.lmbda))


    def forward(self, x, batch):
        k = self.config.hidden_size
        #pass the data from all the convolution layers
        x = [self.conv_list[i](x) for i in range(len(self.config.filter_sizes))]
        #concatenate the result from all the layers
        # [b, 1, 3, k]
        x = tf.keras.layers.concatenate(x,axis=-1)
        #get the total dimension
        total_dims = (k*len(self.config.filter_sizes)-sum(self.config.filter_sizes)+len(self.config.filter_sizes)) * self.config.num_filters
        #reshape the result
        #TODO: fixe the final dimension calculation equation
        x = tf.reshape(x, [batch, -1])
        #perform the dropout
        # x = self.drop(x)
        #pass it through the fully connected layer
        x= self.fc1(x)
        # import pdb; pdb.set_trace()
        return x
        

    def get_loss(self, h, r, t, y):
        """Defines the loss function for the algorithm."""

        h_emb, r_emb, t_emb = self.embed(h, r, t) 
        y = tf.expand_dims(y, -1)

        stacked_h = tf.expand_dims(h_emb, 1)
        stacked_r = tf.expand_dims(r_emb, 1)
        stacked_t = tf.expand_dims(t_emb, 1)

        stacked_hrt = tf.concat([stacked_h, stacked_r, stacked_t], 1)

        stacked_hrt = tf.expand_dims(stacked_hrt, 1) # [b, 1, 3, k]

        predictions = self.forward(stacked_hrt, (1+self.config.neg_rate)*self.config.batch_size)

        loss = tf.reduce_mean(tf.nn.softplus(predictions*y))

        return loss

    def predict(self, h, r, t, topk=-1):
        """Function that performs prediction for TransE. 
           shape of h can be either [num_tot_entity] or [1]. 
           shape of t can be either [num_tot_entity] or [1].

          Returns:
              Tensors: Returns ranks of head and tail.
        """
        h_emb, r_emb, t_emb = self.embed(h, r, t) 
        
        stacked_h = tf.expand_dims(h_emb, 1)
        stacked_r = tf.expand_dims(r_emb, 1)
        stacked_t = tf.expand_dims(t_emb, 1)

        stacked_hrt = tf.concat([stacked_h, stacked_r, stacked_t], 1)
        stacked_hrt = tf.expand_dims(stacked_hrt, 1) # [1, 1, 3, k]

        predictions = self.forward(stacked_hrt, self.config.kg_meta.tot_entity)
        predictions = tf.squeeze(predictions, -1)
        _, rank = tf.nn.top_k(tf.nn.sigmoid(predictions), k=topk)

        return rank

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