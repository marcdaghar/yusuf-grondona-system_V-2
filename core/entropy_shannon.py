
# core/entropy_shannon.py
entropy_shannon = '''"""
Module d'entropie informationnelle (Shannon)
Mesure le désordre dans les systèmes de prix

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import List, Dict


class ShannonEntropy:
    """
    Calcule l'entropie informationnelle de Shannon
    """
    
    @staticmethod
    def price_entropy(prices: List[float], reference_price: float = None) -> float:
        """
        Calcule l'entropie des prix
        H = -Σ(p_i / p̄) * ln(p_i / p̄)
        """
        if not prices:
            return 0.0
        
        if reference_price is None:
            reference_price = np.mean(prices)
        
        if reference_price == 0:
            return 0.0
        
        normalized = np.array(prices) / reference_price
        valid = normalized > 0
        if not any(valid):
            return 0.0
        
        normalized = normalized[valid]
        entropy = -np.sum(normalized * np.log(normalized))
        
        return entropy
    
    @staticmethod
    def exchange_rate_entropy(rates: Dict[str, float], base_rate: float = None) -> float:
        """Calcule l'entropie des taux de change"""
        if not rates:
            return 0.0
        
        values = list(rates.values())
        return ShannonEntropy.price_entropy(values, base_rate)
    
    @staticmethod
    def transaction_entropy(transactions: List[float]) -> float:
        """
        Calcule l'entropie des montants de transaction
        Mesure la diversité des transactions
        """
        if not transactions:
            return 0.0
        
        total = sum(transactions)
        if total == 0:
            return 0.0
        
        probabilities = np.array(transactions) / total
        probabilities = probabilities[probabilities > 0]
        entropy = -np.sum(probabilities * np.log(probabilities))
        
        return entropy
'''

with open("/mnt/agents/output/yusuf-grondona-system/core/entropy_shannon.py", "w") as f:
    f.write(entropy_shannon)

# core/nuqud.py
nuqud = '''"""
Module de gestion des nuqud (monnaie-marchandise or/argent)

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class NuqudReserve:
    """Réserves de nuqud (or/argent)"""
    gold_grams: float = 0.0
    silver_grams: float = 0.0
    gold_price_per_gram: float = 55.0  # USD
    silver_price_per_gram: float = 0.75  # USD
    
    def total_value_usd(self) -> float:
        """Calcule la valeur totale des réserves en USD"""
        gold_value = self.gold_grams * self.gold_price_per_gram
        silver_value = self.silver_grams * self.silver_price_per_gram
        return gold_value + silver_value
    
    def value_in_cbu(self, cbu_price_usd: float) -> float:
        """Calcule la valeur en CBU (Commodity Basket Unit)"""
        if cbu_price_usd == 0:
            return 0.0
        return self.total_value_usd() / cbu_price_usd
    
    def add_gold(self, grams: float) -> None:
        self.gold_grams += grams
    
    def add_silver(self, grams: float) -> None:
        self.silver_grams += grams
    
    def withdraw_gold(self, grams: float) -> bool:
        if self.gold_grams >= grams:
            self.gold_grams -= grams
            return True
        return False
    
    def withdraw_silver(self, grams: float) -> bool:
        if self.silver_grams >= grams:
            self.silver_grams -= grams
            return True
        return False
'''

with open("/mnt/agents/output/yusuf-grondona-system/core/nuqud.py", "w") as f:
    f.write(nuqud)

# core/fulus.py
fulus = '''"""
Module de gestion des fulus (monnaie de vélocité)
Émission et destruction, demurrage (décroissance programmée)

Author: Marc Daghar
License: CC BY-SA 4.0
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FulusWallet:
    """Portefeuille de fulus"""
    address: str
    balance: float
    last_activity: float  # timestamp


class FulusSystem:
    """
    Système de gestion des fulus (monnaie de vélocité)
    
    Caractéristiques:
    - Pas d'intérêt
    - Demurrage (décroissance programmée)
    - Émission contre nuqud
    """
    
    def __init__(self, demurrage_rate: float = 0.025):
        """
        Args:
            demurrage_rate: Taux de décroissance annuel (défaut 2.5%)
        """
        self.wallets: Dict[str, FulusWallet] = {}
        self.total_supply: float = 0.0
        self.demurrage_rate = demurrage_rate
    
    def create_wallet(self, address: str, initial_balance: float = 0.0) -> FulusWallet:
        """Crée un portefeuille fulus"""
        wallet = FulusWallet(
            address=address,
            balance=initial_balance,
            last_activity=0.0
        )
        self.wallets[address] = wallet
        self.total_supply += initial_balance
        return wallet
    
    def issue_fulus(self, address: str, amount: float, 
                   against_nuqud_value: float = 0.0) -> bool:
        """Émet des fulus contre une valeur en nuqud"""
        if address not in self.wallets:
            return False
        
        if against_nuqud_value >= amount:
            self.wallets[address].balance += amount
            self.total_supply += amount
            return True
        return False
    
    def transfer(self, from_addr: str, to_addr: str, amount: float) -> bool:
        """Transfère des fulus d'un portefeuille à l'autre"""
        if from_addr not in self.wallets or to_addr not in self.wallets:
            return False
        
        self.apply_demurrage(from_addr)
        
        if self.wallets[from_addr].balance < amount:
            return False
        
        self.wallets[from_addr].balance -= amount
        self.wallets[to_addr].balance += amount
        
        current_time = 0.0
        self.wallets[from_addr].last_activity = current_time
        self.wallets[to_addr].last_activity = current_time
        
        return True
    
    def apply_demurrage(self, address: str) -> float:
        """Applique le demurrage à un portefeuille"""
        if address not in self.wallets:
            return 0.0
        
        wallet = self.wallets[address]
        time_elapsed = 1.0
        
        decay = wallet.balance * self.demurrage_rate * time_elapsed
        if decay > 0:
            wallet.balance = max(0, wallet.balance - decay)
            self.total_supply -= decay
        
        return decay
    
    def apply_demurrage_all(self) -> Dict[str, float]:
        """Applique le demurrage à tous les portefeuilles"""
        decays = {}
        for address in list(self.wallets.keys()):
            decays[address] = self.apply_demurrage(address)
        return decays
    
    def get_velocity(self, total_transactions: float, period: float = 1.0) -> float:
        """
        Calcule la vélocité des fulus
        V = (P * T) / M
        """
        if self.total_supply == 0:
            return 0.0
        return total_transactions / self.total_supply / period
'''

with open("/mnt/agents/output/yusuf-grondona-system/core/fulus.py", "w") as f:
    f.write(fulus)

print("entropy_shannon.py, nuqud.py, fulus.py créés")