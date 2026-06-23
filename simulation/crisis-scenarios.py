
# simulation/crisis_scenarios.py
crisis_scenarios = '''"""
Module de scénarios de crise
Test des réponses du système Grondona

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import Dict, List, Tuple
from core.grondona_crd import GrondonaCRD


def simulate_invasion_scenario(periods: int = 200) -> List[Dict]:
    """Scénario: invasion bloquant les routes commerciales"""
    crd = GrondonaCRD()
    crd.add_commodity('wheat', floor_price=180, ceiling_price=220, 
                      initial_price=200, initial_stock=1000)
    crd.add_commodity('copper', floor_price=8000, ceiling_price=12000,
                      initial_price=10000, initial_stock=500)
    crd.add_commodity('oil', floor_price=70, ceiling_price=90,
                      initial_price=80, initial_stock=2000)
    
    results = []
    for period in range(periods):
        market_prices = {}
        
        for name, c in crd.commodities.items():
            if period < 100:
                shock = 1 + np.random.normal(0, 0.05)
            else:
                if name == 'wheat':
                    shock = 1 + np.random.normal(0.3, 0.1)
                elif name == 'oil':
                    shock = 1 + np.random.normal(0.5, 0.15)
                else:
                    shock = 1 + np.random.normal(0.1, 0.05)
            
            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])
        
        actions = crd.step(market_prices)
        
        results.append({
            'period': period,
            'money_supply': crd.money_supply,
            'total_stock_value': crd.total_stock_value(),
            'prices': {name: c.current_price for name, c in crd.commodities.items()},
            'stocks': {name: c.stock for name, c in crd.commodities.items()}
        })
    
    return results


def simulate_famine_scenario(periods: int = 200) -> List[Dict]:
    """Scénario: famine causant une chute de la production"""
    crd = GrondonaCRD()
    crd.add_commodity('wheat', floor_price=180, ceiling_price=220,
                      initial_price=200, initial_stock=2000)
    crd.add_commodity('rice', floor_price=160, ceiling_price=200,
                      initial_price=180, initial_stock=1500)
    
    results = []
    for period in range(periods):
        market_prices = {}
        
        for name, c in crd.commodities.items():
            if period < 80:
                shock = 1 + np.random.normal(0, 0.05)
            else:
                shock = 1 + np.random.normal(0.4, 0.1)
            
            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])
        
        actions = crd.step(market_prices)
        
        for name, c in crd.commodities.items():
            consumption = c.stock * 0.01
            c.stock -= consumption
        
        results.append({
            'period': period,
            'money_supply': crd.money_supply,
            'total_stock_value': crd.total_stock_value()
        })
    
    return results


def simulate_panic_scenario(periods: int = 200) -> List[Dict]:
    """Scénario: panique bancaire menant à une ruée sur les dépôts"""
    crd = GrondonaCRD()
    crd.add_commodity('gold', floor_price=1800, ceiling_price=2200,
                      initial_price=2000, initial_stock=100)
    crd.add_commodity('silver', floor_price=25, ceiling_price=30,
                      initial_price=27, initial_stock=500)
    
    results = []
    panic_started = False
    
    for period in range(periods):
        market_prices = {}
        
        for name, c in crd.commodities.items():
            if period < 100:
                shock = 1 + np.random.normal(0, 0.05)
            else:
                if not panic_started:
                    shock = 0.7
                    panic_started = True
                else:
                    shock = 0.9 + 0.1 * (period - 100) / 100
            
            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])
        
        actions = crd.step(market_prices)
        
        results.append({
            'period': period,
            'money_supply': crd.money_supply,
            'total_stock_value': crd.total_stock_value()
        })
    
    return results
'''

with open("/mnt/agents/output/yusuf-grondona-system/simulation/crisis_scenarios.py", "w") as f:
    f.write(crisis_scenarios)

# simulation/stress_test.py
stress_test = '''"""
Module de test de résistance comparant les régimes monétaires

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from simulation.agents import MonetaryModel


def run_stress_test(regime: str, 
                    n_agents: int = 100, 
                    steps: int = 500,
                    shocks: List[Tuple[int, float]] = None) -> Dict:
    """
    Exécute un test de résistance pour un régime donné
    """
    model = MonetaryModel(n_agents=n_agents, regime=regime)
    
    if shocks is None:
        shocks = [
            (100, 0.2),
            (250, 0.3),
            (400, 0.15)
        ]
    
    for step in range(steps):
        shock = 0
        for period, intensity in shocks:
            if step == period:
                shock = intensity
                break
        
        model.step(shock_intensity=shock)
    
    data = model.datacollector.get_model_vars_dataframe()
    
    return {
        'regime': regime,
        'final_gdp': data['GDP'].iloc[-1],
        'mean_gdp': data['GDP'].mean(),
        'gini': data['Gini'].iloc[-1],
        'default_rate': data['DefaultRate'].iloc[-1],
        'total_debt': data['TotalDebt'].iloc[-1],
        'entropy': data['Entropy'].iloc[-1],
        'data': data
    }


def compare_regimes() -> pd.DataFrame:
    """Compare les différents régimes"""
    regimes = [
        'fiat',
        'gold_standard',
        'islamic_no_interest',
        'islamic_no_interest_zakat'
    ]
    
    results = []
    for regime in regimes:
        result = run_stress_test(regime)
        results.append(result)
    
    df = pd.DataFrame([
        {
            'Regime': r['regime'],
            'GDP Final': r['final_gdp'],
            'GDP Moyen': r['mean_gdp'],
            'Gini': r['gini'],
            'Default Rate': r['default_rate'],
            'Total Debt': r['total_debt'],
            'Entropy': r['entropy']
        }
        for r in results
    ])
    
    return df


if __name__ == "__main__":
    df = compare_regimes()
    print("\\n=== COMPARAISON DES RÉGIMES MONÉTAIRES ===\\n")
    print(df.to_string(index=False))
'''

with open("/mnt/agents/output/yusuf-grondona-system/simulation/stress_test.py", "w") as f:
    f.write(stress_test)

# simulation/run_full.py
run_full = '''"""
Script principal pour exécuter une simulation complète

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from core.grondona_crd import GrondonaCRD
from core.entropy_physical import PhysicalEntropy
from simulation.agents import MonetaryModel
from simulation.stress_test import run_stress_test, compare_regimes
from simulation.crisis_scenarios import (
    simulate_invasion_scenario,
    simulate_famine_scenario,
    simulate_panic_scenario
)


def main():
    print("=" * 60)
    print("SYSTÈME YUSUF-GRONDONA - SIMULATION COMPLÈTE")
    print("=" * 60)
    print()
    
    # 1. Simulation du CRD
    print("[1] Simulation du système Grondona")
    crd = GrondonaCRD()
    crd.add_commodity("Blé", floor_price=180, ceiling_price=220, 
                      initial_price=200, initial_stock=1000)
    crd.add_commodity("Cuivre", floor_price=8000, ceiling_price=12000,
                      initial_price=10000, initial_stock=500)
    crd.add_commodity("Coton", floor_price=70, ceiling_price=90,
                      initial_price=80, initial_stock=800)
    
    for period in range(200):
        market_prices = {}
        for name, c in crd.commodities.items():
            shock = 1 + np.random.normal(0, 0.1)
            market_prices[name] = c.current_price * shock
            market_prices[name] = max(0.01, market_prices[name])
        
        crd.step(market_prices)
    
    print(f"  Masse monétaire: {crd.money_supply:.0f}")
    print(f"  Valeur des stocks: {crd.total_stock_value():.0f}")
    print()
    
    # 2. Test de résistance
    print("[2] Test de résistance des régimes")
    df_comparison = compare_regimes()
    print(df_comparison.to_string(index=False))
    print()
    
    # 3. Scénarios de crise
    print("[3] Scénarios de crise")
    invasion_results = simulate_invasion_scenario(100)
    print(f"  Invasion - Masse finale: {invasion_results[-1]['money_supply']:.0f}")
    
    famine_results = simulate_famine_scenario(100)
    print(f"  Famine - Masse finale: {famine_results[-1]['money_supply']:.0f}")
    
    panic_results = simulate_panic_scenario(100)
    print(f"  Panique - Masse finale: {panic_results[-1]['money_supply']:.0f}")
    print()
    
    # 4. Paramètre de bifurcation
    print("[4] Paramètre de bifurcation Λ")
    entropy = PhysicalEntropy()
    
    debt = 1000
    interest_rate = 0.05
    low_entropy = 50
    
    lambda_val = entropy.bifurcation_parameter(debt, interest_rate, low_entropy)
    print(f"  Λ = {lambda_val:.3f}")
    print(f"  Statut: {'⚠️ COLLAPSOLOGIE' if lambda_val > 1 else '✅ STABLE'}")
    print()
    
    # 5. Détection d'absurdités
    print("[5] Détection d'absurdités chrématistiques")
    from core.entropy_physical import detect_chrematistic_absurdity
    
    wti_negative_price = -37.63
    energy_value = 7.2
    
    is_absurd = detect_chrematistic_absurdity(wti_negative_price, energy_value)
    print(f"  Prix WTI négatif (-37.63$) : {'⚠️ ABSURDE' if is_absurd else 'Normal'}")
    print()
    
    print("=" * 60)
    print("SIMULATION TERMINÉE")
    print("=" * 60)


if __name__ == "__main__":
    main()
'''

with open("/mnt/agents/output/yusuf-grondona-system/simulation/run_full.py", "w") as f:
    f.write(run_full)

print("Modules de simulation créés: crisis_scenarios.py, stress_test.py, run_full.py")