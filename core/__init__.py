
# core/__init__.py
init_core = """"""

with open("/mnt/agents/output/yusuf-grondona-system/core/__init__.py", "w") as f:
    f.write(init_core)

# core/entropy_physical.py
entropy_physical = '''"""
Module de thermodynamique économique (Georgescu-Roegen)
Calcul de l'entropie physique et de la négentropie

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import List, Dict, Tuple


class PhysicalEntropy:
    """
    Calcule l'entropie physique d'un système économique
    selon la loi de l'entropie de Georgescu-Roegen
    """
    
    def __init__(self, s_min: float = 0.1, eta: float = 0.05):
        """
        Args:
            s_min: Coût entropique minimum (plancher thermodynamique)
            eta: Coefficient de dissipation (> 0)
        """
        self.s_min = s_min
        self.eta = eta
        self.entropy_history: List[float] = []
    
    def production_entropy(self, quantity: float) -> float:
        """
        Calcule l'entropie produite par un cycle de production
        S_prod = S_min + eta * Q
        """
        return self.s_min + self.eta * quantity
    
    def negentropy_capture(self, stock_variation: float, gamma: float = 0.8) -> float:
        """
        Calcule la négentropie capturée par le stockage
        S_neg = gamma * dV_stock/dt
        """
        return gamma * stock_variation
    
    def total_entropy(self, 
                      initial_entropy: float, 
                      production_quantities: List[float],
                      stock_variations: List[float],
                      gamma: float = 0.8) -> List[float]:
        """
        Calcule l'évolution de l'entropie totale sur une séquence
        S_total(t) = S0 + ∫(S_prod - S_neg) dt
        """
        entropy = [initial_entropy]
        
        for q, dv in zip(production_quantities, stock_variations):
            s_prod = self.production_entropy(q)
            s_neg = self.negentropy_capture(dv, gamma)
            new_entropy = entropy[-1] + (s_prod - s_neg)
            entropy.append(max(0, new_entropy))
        
        return entropy
    
    def bifurcation_parameter(self, 
                              debt: float, 
                              interest_rate: float, 
                              low_entropy_extraction: float) -> float:
        """
        Calcule le paramètre de bifurcation Λ
        Λ = (D * r) / E_dot_low
        """
        if low_entropy_extraction == 0:
            return float('inf')
        return (debt * interest_rate) / low_entropy_extraction
    
    def collapse_threshold(self, 
                           initial_debt: float,
                           interest_rate: float,
                           low_entropy_extraction: float,
                           time_horizon: int = 100) -> Tuple[float, bool]:
        """
        Détermine si et quand le système s'effondre (Λ > 1)
        """
        debt = initial_debt
        
        for t in range(time_horizon):
            lambda_val = self.bifurcation_parameter(debt, interest_rate, low_entropy_extraction)
            if lambda_val > 1.0:
                return t, True
            debt *= (1 + interest_rate)
        
        return time_horizon, False
    
    def find_critical_interest_rate(self, 
                                   debt: float,
                                   low_entropy_extraction: float,
                                   max_interest: float = 0.1,
                                   precision: float = 0.0001) -> float:
        """Trouve le taux d'intérêt critique où Λ = 1"""
        low = 0.0
        high = max_interest
        
        while high - low > precision:
            mid = (low + high) / 2
            if self.bifurcation_parameter(debt, mid, low_entropy_extraction) > 1.0:
                high = mid
            else:
                low = mid
        
        return (low + high) / 2


def detect_chrematistic_absurdity(price: float, physical_value: float) -> bool:
    """
    Détecte si un prix est physiquement absurde
    (ex: prix négatif pour un bien d'énergie positive)
    """
    if price < 0 and physical_value > 0:
        return True
    return False
'''

with open("/mnt/agents/output/yusuf-grondona-system/core/entropy_physical.py", "w") as f:
    f.write(entropy_physical)

print("entropy_physical.py créé")