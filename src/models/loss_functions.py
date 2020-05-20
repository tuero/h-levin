import tensorflow as tf
import numpy as np

from abc import ABC
import math

class LossFunction(ABC):
    
    def compute_loss(self, trajectory, model):
        pass
    
    
class ImprovedLevinLoss(LossFunction):
    
    def __init__(self):
        self.cross_entropy_loss = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
    
    def compute_loss(self, trajectory, model):
        images = [s.get_image_representation() for s in trajectory.get_states()]           
        actions_one_hot = tf.one_hot(trajectory.get_actions(), model.get_number_actions())
        _, _, logits = model(np.array(images))
        loss = self.cross_entropy_loss(actions_one_hot, logits)
        
        d = len(trajectory.get_actions()) + 1
        pi = trajectory.get_solution_pi()
        expanded = trajectory.get_non_normalized_expanded()
        
        a = 0
        if pi < 1.0:
            a = (math.log((d+1)/expanded)) / math.log(pi)
        if a < 0:
            a = 0        
        
        loss *= tf.stop_gradient(tf.convert_to_tensor(expanded * a, dtype=tf.float64))

        return loss
    
class LevinLoss(LossFunction):
    
    def __init__(self):
        self.cross_entropy_loss = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
    
    def compute_loss(self, trajectory, model):
        images = [s.get_image_representation() for s in trajectory.get_states()]           
        actions_one_hot = tf.one_hot(trajectory.get_actions(), model.get_number_actions())
        _, _, logits = model(np.array(images))
        loss = self.cross_entropy_loss(actions_one_hot, logits)
        
        loss *= tf.stop_gradient(tf.convert_to_tensor(trajectory.get_expanded(), dtype=tf.float64))

        return loss
    
class CrossEntropyLoss(LossFunction):
    
    def __init__(self):
        self.cross_entropy_loss = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
    
    def compute_loss(self, trajectory, model):
        images = [s.get_image_representation() for s in trajectory.get_states()]
        actions_one_hot = tf.one_hot(trajectory.get_actions(), model.get_number_actions())
        _, _, logits = model(np.array(images))
        return self.cross_entropy_loss(actions_one_hot, logits)
    
class CrossEntropyMSELoss(LossFunction):
    
    def __init__(self):
        self.cross_entropy_loss = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
        self.mse = tf.keras.losses.MeanSquaredError()
    
    def compute_loss(self, trajectory, model):
        images = [s.get_image_representation() for s in trajectory.get_states()]
        actions_one_hot = tf.one_hot(trajectory.get_actions(), model.get_number_actions())
        _, _, logits_pi, logits_h  = model(np.array(images))
        
        loss = self.cross_entropy_loss(actions_one_hot, logits_pi) 
        
        solution_costs_tf = tf.expand_dims(tf.convert_to_tensor(trajectory.get_solution_costs(), dtype=tf.float64), 1)
        loss += self.mse(solution_costs_tf, logits_h)
        
        return loss
    
class LevinMSELoss(LossFunction):
    
    def __init__(self):
        self.cross_entropy_loss = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
        self.mse = tf.keras.losses.MeanSquaredError()
    
    def compute_loss(self, trajectory, model):
        images = [s.get_image_representation() for s in trajectory.get_states()]           
        actions_one_hot = tf.one_hot(trajectory.get_actions(), model.get_number_actions())
        _, _, logits_pi, logits_h  = model(np.array(images))
        loss = self.cross_entropy_loss(actions_one_hot, logits_pi)
        
        loss *= tf.stop_gradient(tf.convert_to_tensor(trajectory.get_expanded(), dtype=tf.float64))
        
        solution_costs_tf = tf.expand_dims(tf.convert_to_tensor(trajectory.get_solution_costs(), dtype=tf.float64), 1)
        loss += self.mse(solution_costs_tf, logits_h)

        return loss
    
class MSELoss(LossFunction):
    
    def __init__(self):
        self.mse = tf.keras.losses.MeanSquaredError()
    
    def compute_loss(self, trajectory, model):
        images = [s.get_image_representation() for s in trajectory.get_states()]           
        logits_h  = model(np.array(images))
        
        solution_costs_tf = tf.expand_dims(tf.convert_to_tensor(trajectory.get_solution_costs(), dtype=tf.float64), 1)
        loss = self.mse(solution_costs_tf, logits_h)

        return loss