import unittest

import sys
sys.path.append("../")

from core.TransE import TransE
from core.TransH import TransH
from core.TransR import TransR
from core.TransD import TransD
from core.ConvE import ConvE
from core.TransM import TransM
from core.SME import SME
from core.Complex import Complex
from core.DistMult import DistMult
from core.KG2E import KG2E
from core.NTN import NTN
from core.ProjE_pointwise import ProjE_pointwise
from core.Rescal import Rescal
from core.RotatE import RotatE
from core.SLM import SLM

from config.config import *
from utils.dataprep import DataPrep
from utils.trainer import Trainer

import tensorflow as tf

class Pykg2vecIT(unittest.TestCase):
    
    def setUp(self):
        print('setup')
        

    def test_Complex(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='complex')

        config = ComplexConfig(batch_size=512, epochs=1, hidden_size=8)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False

        model = Complex(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_ConvE(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='ConvE')

        config = ConvEConfig(batch_size=512, epochs=1)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = ConvE(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_DistMult(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='DistMult')

        config = DistMultConfig(batch_size=512, epochs=1)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = DistMult(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_KG2E_EL(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='KG2E')

        config = KG2EConfig(batch_size=512, epochs=1, distance_measure="expected_likelihood")

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = KG2E(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()

    
    def test_KG2E_KL(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='KG2E')

        config = KG2EConfig(batch_size=512, epochs=1, distance_measure="kl_divergence")

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = KG2E(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_NTN(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='NTN')

        config = NTNConfig(batch_size=512, epochs=1)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = NTN(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()

    
    def test_ProjE(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='ProjE')

        config = ProjE_pointwiseConfig(learning_rate=0.01, batch_size=512, epochs=1)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = ProjE_pointwise(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_RESCAL(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='Rescal')

        config = RescalConfig(batch_size=512, epochs=1)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = Rescal(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()

    
    def test_RotatE(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='RotatE')

        config = RotatEConfig(batch_size=512, epochs=1)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = RotatE(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_SLM(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='SLM')

        config = SLMConfig(batch_size=512, epochs=1)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False


        model = SLM(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_SMEL(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='SME_Linear')

        config = SMEConfig(batch_size=512, epochs=1, hidden_size=8)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False
        config.bilinear = False

        model = SME(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_SMEB(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='SME_Bilinear')

        config = SMEConfig(batch_size=512, epochs=1, hidden_size=8)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.loadFromData = True
        config.save_model = True
        config.disp_result= False
        config.bilinear = True

        model = SME(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_transE(self):
        
        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='TransE')

        config = TransEConfig(batch_size=512, epochs=1, hidden_size=16)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False

        model = TransE(config)

        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()

    
    def test_transH(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='TransH')

        config = TransHConfig(batch_size=512, epochs=1, hidden_size=16)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False
        config.C = 0.125

        model = TransH(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()

    
    def test_transR(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='TransR')

        config = TransRConfig(batch_size=512, epochs=1, ent_hidden_size=8, rel_hidden_size=4)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False

        model = TransR(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()

    
    def test_TransD(self):

        self.data_handler = DataPrep("Freebase15k", sampling="uniform", algo='TransD')

        config = TransDConfig(batch_size=512, epochs=1, ent_hidden_size=8, rel_hidden_size=8)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False

        model = TransD(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def test_TransM(self):

        DataPrep("Freebase15k", sampling="uniform", algo='TransM')

        config = TransMConfig(batch_size=512, epochs=1, hidden_size=8)

        config.test_step = 1
        config.test_num  = 10
        config.gpu_fraction = 0.4
        config.save_model = False
        config.disp_result= False

        model = TransM(config)
        
        trainer = Trainer(model=model)
        trainer.build_model()
        trainer.train_model()


    def tearDown(self):
        print('teardown')
        tf.reset_default_graph()


def suite():
    suite = unittest.TestSuite()

    suite.addTest(Pykg2vecIT('test_Complex'))
    suite.addTest(Pykg2vecIT('test_ConvE'))
    suite.addTest(Pykg2vecIT('test_DistMult'))
    suite.addTest(Pykg2vecIT('test_KG2E_EL'))
    suite.addTest(Pykg2vecIT('test_KG2E_KL'))
    suite.addTest(Pykg2vecIT('test_NTN'))
    suite.addTest(Pykg2vecIT('test_ProjE'))
    suite.addTest(Pykg2vecIT('test_RESCAL'))
    suite.addTest(Pykg2vecIT('test_RotatE'))
    suite.addTest(Pykg2vecIT('test_SLM'))
    suite.addTest(Pykg2vecIT('test_SMEL'))
    suite.addTest(Pykg2vecIT('test_SMEB'))
    suite.addTest(Pykg2vecIT('test_transE'))
    suite.addTest(Pykg2vecIT('test_transH'))
    suite.addTest(Pykg2vecIT('test_transR'))
    suite.addTest(Pykg2vecIT('test_TransD'))
    suite.addTest(Pykg2vecIT('test_TransM'))
    
    return suite

if __name__ == '__main__':
    """ Execute whole test case as a whole """
    runner = unittest.TextTestRunner()
    runner.run(suite())
