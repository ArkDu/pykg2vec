#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge Graph Meta Class
====================================
It provides Abstract class for the Knowledge graph models.
"""

from abc import ABCMeta, abstractmethod
import tensorflow as tf


class ModelMeta:
	""" Meta Class for knowledge graph embedding algorithms"""

	__metaclass__ = ABCMeta

	def __init__(self):
		"""Initialize and create the model to be trained and inferred"""
		pass

	@abstractmethod
	def def_inputs(self):
		"""Function to define the inputs for the model"""
		pass

	@abstractmethod
	def def_parameters(self):
		"""Function to define the parameters for the model"""
		pass

	@abstractmethod
	def def_loss(self):
		"""Function to define how loss is calculated in the model"""
		pass

	@abstractmethod
	def embed(self,h, r, t):
		"""Function to get the embedding value"""
		pass

	@abstractmethod
	def get_embed(self,h, r, t):
		"""Function to get the embedding value in numpy"""
		pass

	@abstractmethod
	def get_proj_embed(self,h, r, t):
		"""Function to get the projected embedding value"""
		pass


class TrainerMeta:
	""" Meta Class for Trainer Module"""
	__metaclass__ = ABCMeta

	def __init__(self):
		"""Initializing and create the model to be trained and inferred"""
		pass

	@abstractmethod
	def build_model(self):
		"""function to compile the model"""
		pass

	@abstractmethod
	def train_model(self):
		"""function to train the model"""
		pass

	@abstractmethod
	def save_model(self, sess):
		"""function to save the model"""
		pass

	@abstractmethod
	def load_model(self, sess):
		"""function to load the model"""
		pass


class VisualizationMeta:
	""" Meta Class for Visualization Module"""
	__metaclass__ = ABCMeta
	
	def __init__(self):
		"""Initializing and create the model to be trained and inferred"""
		pass

	@abstractmethod
	def display(self):
		"""function to display embedding"""
		pass

	@abstractmethod
	def summary(self):
		"""function to print the summary"""
		pass


class EvaluationMeta:
	""" Meta Class for Evaluation Module"""
	__metaclass__ = ABCMeta

	def __init__(self):
		pass

	@abstractmethod
	def relation_prediction(self):
		"""Function for evaluating link prediction"""
		pass

	@abstractmethod
	def entity_classification(self):
		"""Function for evaluating entity classification"""
		pass

	@abstractmethod
	def relation_classification(self):
		"""Function for evaluating relation classification"""
		pass

	@abstractmethod
	def triple_classification(self):
		"""Function for evaluating triple classificaiton"""
		pass

	@abstractmethod
	def entity_completion(self):
		"""Function for evaluating entity completion"""
		pass


class InferenceMeta:
	""" Meta Class for inference based on distance measure"""
	__metaclass__ = ABCMeta

	def __init__(self):
		pass

	@abstractmethod
	def def_parameters(self):
		"""Function to define the parameters for the model"""
		pass

	def distance(self, h, r, t, axis=1):
		"""Function to calculate distance measure in embedding space.

		Args:
			h (Tensor): Head entities ids.
			r (Tensor): Relation ids of the triple.
			t (Tensor): Tail entity ids of the triple.
			axis (int): Determines the axis for reduction

		Returns:
			Tensors: Returns the distance measure.
		"""
		if self.config.L1_flag:
			return tf.reduce_sum(tf.abs(h + r - t), axis=axis)  # L1 norm
		else:
			return tf.reduce_sum((h + r - t) ** 2, axis=axis)  # L2 norm

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

		score_tail = self.distance(head_vec, rel_vec, norm_ent_embeddings, axis=1)
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

		score_head = self.distance(norm_ent_embeddings, rel_vec, tail_vec, axis=1)
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

		score_rel = self.distance(head_vec, norm_rel_embeddings, tail_vec, axis=1)
		_, rels = tf.nn.top_k(-score_rel, k=topk)

		return rels

