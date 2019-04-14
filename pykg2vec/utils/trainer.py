import sys
sys.path.append("../")
from core.KGMeta import ModelMeta, TrainerMeta
import pandas as pd
import tensorflow as tf
import timeit
from argparse import ArgumentParser
import os
from utils.evaluation import Evaluation


class Trainer(TrainerMeta):

    def __init__(self, model):
        self.model = model
        self.config = self.model.config
        self.data_handler = self.model.data_handler

        self.evaluator = Evaluation(model=model, test_data='test')
        self.training_results = []
    
    def build_model(self):
        """function to build the model"""
        self.sess = tf.Session(config=self.config.gpu_config)
        self.global_step = tf.Variable(0, name="global_step", trainable=False)
        
        if self.config.optimizer == 'gradient':
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=self.config.learning_rate)
        elif self.config.optimizer == 'rms':
            optimizer = tf.train.RMSPropOptimizer(learning_rate=self.config.learning_rate)
        elif self.config.optimizer == 'adam':
            optimizer = tf.train.AdamOptimizer(learning_rate=self.config.learning_rate)
        else:
            raise NotImplementedError("No support for %s optimizer" % self.config.optimizer)

        grads = optimizer.compute_gradients(self.model.loss)
        self.op_train = optimizer.apply_gradients(grads, global_step=self.global_step)
        self.sess.run(tf.global_variables_initializer())
    
    def train_model(self):
        """function to train the model"""
        if self.config.loadFromData:
            self.load_model()
            self.tiny_test(0) # test the saved model 
        else:
            for n_iter in range(self.config.epochs):
                self.train_model_epoch(n_iter)                
                self.tiny_test(n_iter)

            self.evaluator.save_test_summary(algo=self.model.model_name)
            self.evaluator.save_training_result(self.training_results)

            if self.config.save_model:
                self.save_model()
                   
        if self.config.disp_result:
            self.model.display(self.sess)

        if self.config.disp_summary:
            self.model.summary()

    def train_model_epoch(self, epoch_idx):
        acc_loss = 0
        num_batch = len(self.data_handler.train_triples_ids) // self.config.batch_size
        start_time = timeit.default_timer()
        
        gen_train = self.data_handler.batch_generator_train(batch_size=self.config.batch_size)

        for batch_idx in range(num_batch):

            ph, pr, pt, nh, nr, nt = next(gen_train)

            feed_dict = {
                self.model.pos_h: ph,
                self.model.pos_t: pt,
                self.model.pos_r: pr,
                self.model.neg_h: nh,
                self.model.neg_t: nt,
                self.model.neg_r: nr
            }

            _, step, loss = self.sess.run([self.op_train, self.global_step, self.model.loss], feed_dict)

            acc_loss += loss
            
            print('[%.2f sec](%d/%d): -- loss: %.5f' % (timeit.default_timer() - start_time,
                                                        batch_idx, num_batch, loss), end='\r')

        print('iter[%d] ---Train Loss: %.5f ---time: %.2f' % (
            epoch_idx, acc_loss, timeit.default_timer() - start_time))

        self.training_results.append([epoch_idx, acc_loss])

    def tiny_test(self, curr_epoch):
        if curr_epoch % self.config.test_step == 0 or \
           curr_epoch == 0 or \
           curr_epoch == self.config.epochs - 1:

            self.evaluator.test(self.sess, curr_epoch)
            self.evaluator.print_test_summary(curr_epoch)

    def full_test(self):
        self.evaluator.test(self.sess, self.config.epochs)
        self.evaluator.print_test_summary(self.config.epochs)

    def save_model(self):
        """function to save the model"""
        if not os.path.exists(self.config.tmp):
            os.mkdir('../intermediate')
        saver = tf.train.Saver(self.model.parameter_list)
        saver.save(self.sess, self.config.tmp + '/%s.vec' % self.model.model_name)

    def load_model(self):
        """function to load the model"""
        if not os.path.exists(self.config.tmp):
            os.mkdir('../intermediate')
        saver = tf.train.Saver(self.model.parameter_list)
        saver.restore(self.sess, self.config.tmp + '/%s.vec' % self.model.model_name)