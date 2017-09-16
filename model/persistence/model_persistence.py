# -*- coding: utf-8; -*-
# Copyright (c) 2017, Daniel Falci - danielfalci@gmail.com
# Laboratory for Advanced Information Systems - LAIS
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of deep_pt_srl nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os

from keras.models import model_from_json

from model.configuration import Config


class ModelPersistence(object):

    def __init__(self):
        """
        Saves and loads a neural network model
        :param nn:
        :param modelFile:
        :param weightFile:
        :return:
        """
        self.state = 0


    def save(self, nn, modelFile, weightFile):
        nn_json = nn.to_json()
        with open(modelFile, 'w') as json_file:
            json_file.write(nn_json)
            json_file.close()
        nn.save_weights(weightFile)

    def delete(self, modelFile, weightFile):
        try:
            os.remove(modelFile)
            os.remove(weightFile)
        except:
            print 'error removing file'
            pass

    def load(self, modelFile, weightFile):
        json_file = open(modelFile, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        nn = model_from_json(loaded_model_json)

        nn.load_weights(weightFile)
        self.state = 1
        return nn

class ModelEvaluation(object):

    def __init__(self, numberToKeep=30):
        self.bestEpoch = None
        self.maxF1 = 0
        self.persistence = ModelPersistence()
        self.pattern = Config.Instance().resultsDir+'/model_'
        self.numberToKeep = numberToKeep
        self.savedFiles = []


    def __getNames(self, epoch):
        return (self.pattern+str(epoch)+'.json',self.pattern+str(epoch)+'.h5py')

    def __save(self, nn, epoch):
        modelFile, wFile = self.__getNames(epoch)
        self.persistence.save(nn, modelFile, wFile)
        self.savedFiles.append((modelFile, wFile))
        print 'Checkpoint saved'
        self.__removeIfNeeded()

    def __removeIfNeeded(self):
        if len(self.savedFiles) > self.numberToKeep:
            item = self.savedFiles.pop(0)
            print 'removing {} - {}'.format(item[0], item[1])
            self.persistence.delete(item[0], item[1])
            print 'files have been removed'


    def update(self, nn, f1, epoch, fixedCheckPoint=10):
        if f1 > self.maxF1:
            print 'NEW BEST VALUE IN EPOCH {} : {} \nSaving checkpoint...'.format(epoch, f1)
            if self.bestEpoch!=None:
                modelFile, wFile = self.__getNames(self.bestEpoch)
                self.persistence.delete(modelFile, wFile)

            self.__save(nn, epoch)

            self.bestEpoch = epoch
            self.maxF1 = f1
        else:
            if epoch % fixedCheckPoint ==0 and epoch > 0:
                print 'Fixed checkpoint {}'.format(fixedCheckPoint)
                self.__save(nn, epoch)
            else:
                print 'Not saving'