
# core/grondona_crd.py
grondona_crd = '''"""
Module du système Grondona (Commodity Reserve Department)
Gestion des prix plancher/plafond et des stockpiles

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Commodity:
    """Matière première dans le panier CBU"""
    name: str
    floor_price: float
    ceiling_price: float
    current_price: float
    stock: float
    elasticity: float = 1.0
    storage_cost: float = 0.005


class GrondonaCRD:
    """
    Commodity Reserve Department basé sur le système Grondona
    
    Mécanisme:
    - Prix < plancher: achat (expansion monétaire)
    - Prix > plafond: vente (contraction monétaire)
    """
    
    def __init__(self):
        self.commodities: Dict[str, Commodity] = {}
        self.money_supply: float = 0.0
        self.history: List[Dict] = []
    
    def add_commodity(self, 
                      name: str,
                      floor_price: float,
                      ceiling_price: float,
                      initial_price: float,
                      initial_stock: float = 0.0,
                      elasticity: float = 1.0) -> None:
        """Ajoute une matière première au CRD"""
        self.commodities[name] = Commodity(
            name=name,
            floor_price=floor_price,
            ceiling_price=ceiling_price,
            current_price=initial_price,
            stock=initial_stock,
            elasticity=elasticity
        )
    
    def step(self, market_prices: Dict[str, float]) -> Dict[str, Dict]:
        """
        Effectue une itération du système Grondona
        
        Returns:
            Dictionnaire des actions effectuées
        """
        actions = {}
        
        for name, price in market_prices.items():
            if name not in self.commodities:
                continue
            
            commodity = self.commodities[name]
            action = {
                'name': name,
                'action': 'none',
                'quantity': 0.0,
                'price': price,
                'money_flow': 0.0,
                'new_stock': commodity.stock
            }
            
            if price < commodity.floor_price:
                # Achat : expansion monétaire
                purchase_qty = (commodity.floor_price - price) * commodity.elasticity
                commodity.stock += purchase_qty
                self.money_supply += purchase_qty * commodity.floor_price
                
                action['action'] = 'buy'
                action['quantity'] = purchase_qty
                action['money_flow'] = purchase_qty * commodity.floor_price
                action['new_stock'] = commodity.stock
                
            elif price > commodity.ceiling_price:
                # Vente : contraction monétaire
                sale_qty = min(
                    commodity.stock,
                    (price - commodity.ceiling_price) * commodity.elasticity
                )
                commodity.stock -= sale_qty
                self.money_supply -= sale_qty * commodity.ceiling_price
                
                action['action'] = 'sell'
                action['quantity'] = sale_qty
                action['money_flow'] = -sale_qty * commodity.ceiling_price
                action['new_stock'] = commodity.stock
            
            commodity.current_price = price
            
            # Appliquer les coûts de stockage
            commodity.stock *= (1 - commodity.storage_cost)
            
            actions[name] = action
        
        self._log_state(actions)
        
        return actions
    
    def _log_state(self, actions: Dict) -> None:
        """Enregistre l'état du CRD"""
        state = {
            'money_supply': self.money_supply,
            'commodities': {
                name: {
                    'stock': c.stock,
                    'price': c.current_price,
                    'floor': c.floor_price,
                    'ceiling': c.ceiling_price
                }
                for name, c in self.commodities.items()
            },
            'actions': actions
        }
        self.history.append(state)
    
    def total_stock_value(self) -> float:
        """Calcule la valeur totale des stockpiles"""
        total = 0.0
        for c in self.commodities.values():
            total += c.stock * c.current_price
        return total
    
    def get_entropy_bound(self) -> float:
        """Calcule la borne d'entropie du système"""
        total_value = self.total_stock_value()
        if total_value == 0:
            return 0.0
        
        shares = [c.stock * c.current_price / total_value for c in self.commodities.values()]
        shares = [s for s in shares if s > 0]
        
        if not shares:
            return 0.0
        
        return -np.sum(shares * np.log(shares))


def simulate_crd(initial_prices: Dict[str, float],
                 price_volatility: float = 0.15,
                 periods: int = 100,
                 floor_ratio: float = 0.8,
                 ceiling_ratio: float = 1.2) -> List[Dict]:
    """
    Simule le système Grondona sur une période donnée
    """
    crd = GrondonaCRD()
    
    for name, price in initial_prices.items():
        crd.add_commodity(
            name=name,
            floor_price=price * floor_ratio,
            ceiling_price=price * ceiling_ratio,
            initial_price=price,
            initial_stock=100.0
        )
    
    results = []
    for period in range(periods):
        market_prices = {}
        for name, c in crd.commodities.items():
            shock = 1 + np.random.normal(0, price_volatility)
            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])
        
        actions = crd.step(market_prices)
        results.append({
            'period': period,
            'money_supply': crd.money_supply,
            'total_value': crd.total_stock_value(),
            'actions': actions
        })
    
    return results
'''

with open("/mnt/agents/output/yusuf-grondona-system/core/grondona_crd.py", "w") as f:
    f.write(grondona_crd)

# core/hisba.py
hisba = '''"""
Module d'inspection du marché (Hisba)
Régulation par le muhtassib

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class MarketViolation:
    """Violation détectée sur le marché"""
    type: str
    severity: float  # 0-1
    description: str
    evidence: Dict


class HisbaInstitution:
    """
    Institution de régulation du marché (Hisba)
    Inspirée du muhtassib traditionnel
    """
    
    def __init__(self):
        self.violations: List[MarketViolation] = []
        self.inspections: List[Dict] = []
        self.weights_and_measures: Dict[str, float] = {}
        self.fraud_scores: Dict[str, float] = {}
    
    def inspect_weights_and_measures(self, 
                                     item_name: str,
                                     declared_weight: float,
                                     actual_weight: float) -> bool:
        """Vérifie que les poids et mesures sont conformes"""
        tolerance = 0.01  # 1%
        is_valid = abs(declared_weight - actual_weight) <= tolerance * declared_weight
        
        if not is_valid:
            violation = MarketViolation(
                type='weight_fraud',
                severity=min(1.0, abs(declared_weight - actual_weight) / declared_weight),
                description=f"Poids déclaré {declared_weight} vs mesuré {actual_weight}",
                evidence={'item': item_name, 'declared': declared_weight, 'actual': actual_weight}
            )
            self.violations.append(violation)
        
        return is_valid
    
    def detect_market_manipulation(self, 
                                 prices: Dict[str, float],
                                 historical_prices: Dict[str, List[float]],
                                 threshold: float = 2.0) -> List[MarketViolation]:
        """Détecte les manipulations de marché (prix aberrants)"""
        violations = []
        
        for item, current_price in prices.items():
            if item not in historical_prices:
                continue
            
            hist = historical_prices[item]
            if len(hist) < 3:
                continue
            
            mean_price = np.mean(hist[-10:]) if len(hist) >= 10 else np.mean(hist)
            std_price = np.std(hist[-10:]) if len(hist) >= 10 else np.std(hist)
            
            if std_price > 0 and abs(current_price - mean_price) > threshold * std_price:
                violation = MarketViolation(
                    type='price_manipulation',
                    severity=min(1.0, abs(current_price - mean_price) / (threshold * std_price)),
                    description=f"Prix aberrant pour {item}: {current_price} vs moyenne {mean_price}",
                    evidence={'item': item, 'price': current_price, 'mean': mean_price}
                )
                violations.append(violation)
                self.violations.append(violation)
        
        return violations
    
    def inspect_fraudulent_bidding(self, 
                                 bids: List[float],
                                 ask: float) -> bool:
        """Détecte les enchères frauduleuses (najsh)"""
        if len(bids) < 2:
            return True
        
        mean_bid = np.mean(bids)
        max_bid = max(bids)
        
        if max_bid > mean_bid * 1.5 and max_bid > ask * 0.9:
            violation = MarketViolation(
                type='fraudulent_bidding',
                severity=min(1.0, (max_bid - mean_bid) / mean_bid),
                description=f"Enchère suspecte: max {max_bid} vs moyenne {mean_bid}",
                evidence={'bids': bids, 'ask': ask}
            )
            self.violations.append(violation)
            return False
        
        return True
    
    def get_honesty_score(self, merchant_id: str) -> float:
        """Calcule un score d'honnêteté pour un commerçant"""
        score = 1.0
        for v in self.violations:
            if merchant_id in str(v.evidence):
                score *= (1 - v.severity)
        
        self.fraud_scores[merchant_id] = score
        return score
    
    def report_annual(self) -> Dict:
        """Génère un rapport annuel d'inspection"""
        return {
            'total_violations': len(self.violations),
            'violations_by_type': {
                t: sum(1 for v in self.violations if v.type == t)
                for t in set(v.type for v in self.violations)
            },
            'average_severity': np.mean([v.severity for v in self.violations]) if self.violations else 0,
            'honesty_scores': self.fraud_scores
        }
'''

with open("/mnt/agents/output/yusuf-grondona-system/core/hisba.py", "w") as f:
    f.write(hisba)

print("grondona_crd.py et hisba.py créés")