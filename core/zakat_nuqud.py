
# core/zakat_nuqud.py
zakat_nuqud = '''"""
Module de Zakat payable en nuqud (or/argent)
Gestion du Bayt al-Mal

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ZakatBeneficiary:
    """Bénéficiaire de la Zakat"""
    category: str  # 8 catégories du Coran (9:60)
    amount_received: float
    description: str


class ZakatSystem:
    """
    Système de Zakat
    - Collecte en nuqud (or/argent)
    - Distribution aux 8 catégories du Coran
    """
    
    QURANIC_CATEGORIES = [
        'al_fuqara',      # Les pauvres
        'al_masakin',     # Les nécessiteux
        'al_amilin',      # Les collecteurs de zakat
        'al_muallafati',  # Ceux dont les cœurs sont à rallier
        'fi_al_riqab',    # Les affranchis
        'al_gharimin',    # Les endettés
        'fi_sabil_allah', # La voie de Dieu
        'ibn_al_sabil'    # Les voyageurs en détresse
    ]
    
    def __init__(self, nisab_gold_grams: float = 85.0, 
                 nisab_silver_grams: float = 595.0,
                 rate: float = 0.025):
        """
        Args:
            nisab_gold_grams: Seuil d'or pour le nisab
            nisab_silver_grams: Seuil d'argent pour le nisab
            rate: Taux de zakat (2.5%)
        """
        self.nisab_gold = nisab_gold_grams
        self.nisab_silver = nisab_silver_grams
        self.rate = rate
        self.total_collected_gold: float = 0.0
        self.total_collected_silver: float = 0.0
        self.distributions: Dict[str, List[ZakatBeneficiary]] = {
            category: [] for category in self.QURANIC_CATEGORIES
        }
        self.history: List[Dict] = []
    
    def compute_zakat(self, 
                      gold_grams: float, 
                      silver_grams: float,
                      cash_equivalent: float = 0.0,
                      trade_goods_value: float = 0.0) -> Tuple[float, float]:
        """Calcule la zakat due en or et en argent"""
        total_value = (gold_grams * 55.0 + silver_grams * 0.75 + 
                       cash_equivalent + trade_goods_value)
        nisab_value = self.nisab_silver * 0.75
        
        if total_value < nisab_value:
            return 0.0, 0.0
        
        zakat_value = total_value * self.rate
        
        gold_value = gold_grams * 55.0
        silver_value = silver_grams * 0.75
        
        if gold_value + silver_value > 0:
            gold_zakat = zakat_value * (gold_value / (gold_value + silver_value))
            silver_zakat = zakat_value * (silver_value / (gold_value + silver_value))
        else:
            gold_zakat = 0.0
            silver_zakat = zakat_value / 0.75
        
        return gold_zakat, silver_zakat
    
    def collect_zakat(self, 
                      gold_grams: float, 
                      silver_grams: float,
                      payer_id: str) -> Dict:
        """Collecte la zakat auprès d'un payeur"""
        gold_zakat, silver_zakat = self.compute_zakat(gold_grams, silver_grams)
        
        result = {
            'payer_id': payer_id,
            'gold_collected': gold_zakat,
            'silver_collected': silver_zakat,
            'success': True
        }
        
        if gold_zakat > 0 or silver_zakat > 0:
            self.total_collected_gold += gold_zakat
            self.total_collected_silver += silver_zakat
            self.history.append(result)
            self._auto_distribute(gold_zakat, silver_zakat)
        
        return result
    
    def _auto_distribute(self, gold: float, silver: float) -> None:
        """Distribue automatiquement selon les 8 catégories"""
        total_value = gold * 55.0 + silver * 0.75
        share = total_value / len(self.QURANIC_CATEGORIES)
        
        for category in self.QURANIC_CATEGORIES:
            beneficiary = ZakatBeneficiary(
                category=category,
                amount_received=share,
                description=f"Distribution automatique"
            )
            self.distributions[category].append(beneficiary)
    
    def distribute_manually(self, 
                            category: str, 
                            amount_gold: float,
                            amount_silver: float,
                            recipient: str) -> bool:
        """Distribution manuelle à une catégorie spécifique"""
        if category not in self.QURANIC_CATEGORIES:
            return False
        
        if amount_gold > 0 and self.total_collected_gold >= amount_gold:
            self.total_collected_gold -= amount_gold
        elif amount_silver > 0 and self.total_collected_silver >= amount_silver:
            self.total_collected_silver -= amount_silver
        else:
            return False
        
        beneficiary = ZakatBeneficiary(
            category=category,
            amount_received=amount_gold * 55.0 + amount_silver * 0.75,
            description=f"Distribution à {recipient}"
        )
        self.distributions[category].append(beneficiary)
        return True
    
    def get_report(self) -> Dict:
        """Rapport du Bayt al-Mal"""
        return {
            'total_collected_gold': self.total_collected_gold,
            'total_collected_silver': self.total_collected_silver,
            'total_value_usd': self.total_collected_gold * 55.0 + self.total_collected_silver * 0.75,
            'distributions': {
                category: len(items) for category, items in self.distributions.items()
            },
            'history_count': len(self.history)
        }
'''

with open("/mnt/agents/output/yusuf-grondona-system/core/zakat_nuqud.py", "w") as f:
    f.write(zakat_nuqud)

# core/zakat.py
zakat = '''"""
Module de Zakat simplifié

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from typing import List
from dataclasses import dataclass


@dataclass
class ZakatPayer:
    """Payeur de Zakat"""
    name: str
    wealth: float
    gold_grams: float
    silver_grams: float


def calculate_zakat(
    nuqud_holdings: List,
    trade_profit_nuqud: float,
    agricultural_yield_nuqud: float,
    livestock_nuqud: float
) -> float:
    """
    Calcule la Zakat due en nuqud
    
    Taux:
    - Or/argent/cash: 2.5% (1/40)
    - Produits agricoles: 10% (arrosage naturel) ou 5% (arrosage artificiel)
    - Bétail: seuils spécifiques
    """
    total = 0.0
    
    # Zakat sur l'épargne (nuqud)
    for n in nuqud_holdings:
        if hasattr(n, 'is_zakatable') and n.is_zakatable():
            total += n.value_in_silver_grams() * 0.025
    
    # Zakat sur le profit du commerce
    total += trade_profit_nuqud * 0.025
    
    # Zakat sur les produits agricoles (10%)
    total += agricultural_yield_nuqud * 0.10
    
    # Zakat sur le bétail (simplifié)
    total += livestock_nuqud * 0.025
    
    return total
'''

with open("/mnt/agents/output/yusuf-grondona-system/core/zakat.py", "w") as f:
    f.write(zakat)

print("zakat_nuqud.py et zakat.py créés")