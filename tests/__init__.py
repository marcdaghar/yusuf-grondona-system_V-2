
# tests/__init__.py
open("/mnt/agents/output/yusuf-grondona-system/tests/__init__.py", "w").close()

# tests/test_core.py
test_core = '''"""
Tests unitaires pour les modules core

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from core.grondona_crd import GrondonaCRD, simulate_crd
from core.entropy_physical import PhysicalEntropy, detect_chrematistic_absurdity
from core.nuqud import NuqudReserve
from core.fulus import FulusSystem
from core.hisba import HisbaInstitution
from core.zakat_nuqud import ZakatSystem


class TestGrondonaCRD:
    """Tests pour le CRD"""
    
    def test_crd_initialization(self):
        crd = GrondonaCRD()
        crd.add_commodity("Test", floor_price=100, ceiling_price=200,
                          initial_price=150, initial_stock=100)
        
        assert len(crd.commodities) == 1
        assert crd.commodities["Test"].stock == 100
        assert crd.commodities["Test"].floor_price == 100
        assert crd.commodities["Test"].ceiling_price == 200
    
    def test_crd_buy_action(self):
        crd = GrondonaCRD()
        crd.add_commodity("Test", floor_price=100, ceiling_price=200,
                          initial_price=150, initial_stock=100)
        
        actions = crd.step({"Test": 80})
        
        assert actions["Test"]["action"] == "buy"
        assert actions["Test"]["quantity"] > 0
        assert crd.money_supply > 0
    
    def test_crd_sell_action(self):
        crd = GrondonaCRD()
        crd.add_commodity("Test", floor_price=100, ceiling_price=200,
                          initial_price=150, initial_stock=100)
        
        actions = crd.step({"Test": 250})
        
        assert actions["Test"]["action"] == "sell"
        assert actions["Test"]["quantity"] > 0
    
    def test_crd_simulation(self):
        initial_prices = {"Blé": 200, "Cuivre": 10000, "Coton": 80}
        results = simulate_crd(initial_prices, periods=50)
        
        assert len(results) == 50
        assert results[0]["money_supply"] >= 0
        assert results[-1]["money_supply"] >= 0


class TestEntropy:
    """Tests pour l'entropie physique"""
    
    def test_bifurcation_stable(self):
        entropy = PhysicalEntropy()
        
        lambda_val = entropy.bifurcation_parameter(
            debt=100, interest_rate=0.03, low_entropy_extraction=10
        )
        assert lambda_val < 1.0
    
    def test_bifurcation_unstable(self):
        entropy = PhysicalEntropy()
        
        lambda_val = entropy.bifurcation_parameter(
            debt=100, interest_rate=0.03, low_entropy_extraction=1
        )
        assert lambda_val > 1.0
    
    def test_collapse_detection(self):
        entropy = PhysicalEntropy()
        
        t, collapsed = entropy.collapse_threshold(
            initial_debt=1000, interest_rate=0.05, low_entropy_extraction=10
        )
        assert collapsed == True
        assert t < 100
    
    def test_negative_price_detection(self):
        assert detect_chrematistic_absurdity(-37.63, 7.2) is True
        assert detect_chrematistic_absurdity(70.0, 7.2) is False
    
    def test_total_entropy(self):
        entropy = PhysicalEntropy()
        result = entropy.total_entropy(
            initial_entropy=0.5,
            production_quantities=[10, 12, 8],
            stock_variations=[5, -2, 3]
        )
        assert len(result) == 4
        assert all(r >= 0 for r in result)


class TestNuqud:
    """Tests pour les nuqud"""
    
    def test_nuqud_value(self):
        reserve = NuqudReserve(gold_grams=100, silver_grams=500)
        value = reserve.total_value_usd()
        expected = 100 * 55.0 + 500 * 0.75
        assert value == expected
    
    def test_nuqud_withdrawal(self):
        reserve = NuqudReserve(gold_grams=100, silver_grams=500)
        
        assert reserve.withdraw_gold(50) == True
        assert reserve.gold_grams == 50
        
        assert reserve.withdraw_gold(100) == False
        assert reserve.gold_grams == 50


class TestFulus:
    """Tests pour les fulus"""
    
    def test_fulus_creation(self):
        system = FulusSystem()
        wallet = system.create_wallet("addr1", 1000)
        assert wallet.balance == 1000
        assert system.total_supply == 1000
    
    def test_fulus_transfer(self):
        system = FulusSystem()
        system.create_wallet("addr1", 1000)
        system.create_wallet("addr2", 0)
        
        result = system.transfer("addr1", "addr2", 500)
        assert result == True
        assert system.wallets["addr1"].balance == 500
        assert system.wallets["addr2"].balance == 500
    
    def test_fulus_demurrage(self):
        system = FulusSystem(demurrage_rate=0.025)
        system.create_wallet("addr1", 1000)
        
        decay = system.apply_demurrage("addr1")
        assert decay > 0
        assert system.wallets["addr1"].balance < 1000


class TestHisba:
    """Tests pour l'inspection du marché"""
    
    def test_weight_inspection(self):
        hisba = HisbaInstitution()
        result = hisba.inspect_weights_and_measures("wheat", 100, 100.5)
        assert result == True
        
        result = hisba.inspect_weights_and_measures("wheat", 100, 95)
        assert result == False
        assert len(hisba.violations) == 1
    
    def test_price_manipulation(self):
        hisba = HisbaInstitution()
        prices = {"wheat": 300}
        historical = {"wheat": [200, 210, 205, 215, 220] * 10}
        
        violations = hisba.detect_market_manipulation(prices, historical)
        assert len(violations) > 0


class TestZakat:
    """Tests pour la Zakat"""
    
    def test_zakat_computation(self):
        zakat = ZakatSystem()
        gold_zakat, silver_zakat = zakat.compute_zakat(
            gold_grams=100, silver_grams=500,
            cash_equivalent=1000, trade_goods_value=500
        )
        assert gold_zakat > 0 or silver_zakat > 0
    
    def test_zakat_collection(self):
        zakat = ZakatSystem()
        result = zakat.collect_zakat(gold_grams=100, silver_grams=500, payer_id="payer1")
        
        assert result["success"] == True
        assert zakat.total_collected_gold > 0 or zakat.total_collected_silver > 0
    
    def test_zakat_report(self):
        zakat = ZakatSystem()
        zakat.collect_zakat(gold_grams=100, silver_grams=500, payer_id="payer1")
        report = zakat.get_report()
        
        assert report["total_collected_gold"] > 0
        assert report["history_count"] == 1
'''

with open("/mnt/agents/output/yusuf-grondona-system/tests/test_core.py", "w") as f:
    f.write(test_core)

# tests/test_agents.py
test_agents = '''"""
Tests unitaires pour les agents de simulation

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from simulation.agents import HouseholdAgent, FinancialAgent, MonetaryModel
from simulation.yusuf_model import YusufConfig, YusufSystem, CapitalistSystem


class TestHouseholdAgent:
    """Tests pour l'agent ménage"""
    
    def test_production(self):
        model = MonetaryModel(n_agents=1)
        agent = [a for a in model.schedule.agents if isinstance(a, HouseholdAgent)][0]
        
        initial_wealth = agent.wealth
        output = agent.produce()
        
        assert output > 0
        assert agent.wealth > initial_wealth
    
    def test_consumption(self):
        model = MonetaryModel(n_agents=1)
        agent = [a for a in model.schedule.agents if isinstance(a, HouseholdAgent)][0]
        
        initial_wealth = agent.wealth
        agent.produce()
        consumption = agent.consume_and_save()
        
        assert consumption > 0
        assert consumption <= initial_wealth + agent.production
    
    def test_zakat_payment(self):
        model = MonetaryModel(n_agents=1)
        agent = [a for a in model.schedule.agents if isinstance(a, HouseholdAgent)][0]
        
        agent.wealth = 200  # Above nisab
        zakat = agent.pay_zakat(rate=0.025, nisab=100)
        
        assert zakat > 0
        assert agent.wealth == 200 - zakat
    
    def test_mudaraba(self):
        model = MonetaryModel(n_agents=1)
        agent = [a for a in model.schedule.agents if isinstance(a, HouseholdAgent)][0]
        
        agent.wealth = 1000
        result = agent.mudaraba_invest(500, profit_share_ratio=0.7, risk_factor=0.0)
        
        assert result != 0


class TestMonetaryModel:
    """Tests pour le modèle monétaire"""
    
    def test_gini_computation(self):
        model = MonetaryModel(n_agents=100)
        gini = model.compute_gini()
        
        assert 0 <= gini <= 1
    
    def test_gdp_computation(self):
        model = MonetaryModel(n_agents=10)
        
        for _ in range(10):
            model.step()
        
        gdp = model.compute_gdp()
        assert gdp >= 0
    
    def test_default_rate(self):
        model = MonetaryModel(n_agents=10)
        
        for _ in range(50):
            model.step(shock_intensity=0.5)
        
        default_rate = model.compute_default_rate()
        assert 0 <= default_rate <= 1
    
    def test_run_simulation(self):
        model = MonetaryModel(n_agents=10)
        data = model.run_simulation(steps=20)
        
        assert len(data) == 20
        assert "GDP" in data.columns
        assert "Gini" in data.columns


class TestYusufModel:
    """Tests pour le modèle Yusuf"""
    
    def test_yusuf_vs_capitalist(self):
        config = YusufConfig(T=50, dt=0.5)
        
        yusuf = YusufSystem(config)
        capitalist = CapitalistSystem(config)
        
        y_res = yusuf.run()
        c_res = capitalist.run()
        
        assert y_res.solvency_rate >= c_res.solvency_rate
        assert y_res.consumption_volatility <= c_res.consumption_volatility
    
    def test_yusuf_solvency(self):
        config = YusufConfig(T=100, dt=0.5)
        yusuf = YusufSystem(config)
        res = yusuf.run()
        
        assert res.solvency_rate == 100.0
    
    def test_monte_carlo(self):
        config = YusufConfig(T=20, dt=1.0)
        comparator = YusufConfig()
        
        # Simple test that it runs without error
        yusuf = YusufSystem(config)
        res = yusuf.run()
        assert res.final_stock >= 0
'''

with open("/mnt/agents/output/yusuf-grondona-system/tests/test_agents.py", "w") as f:
    f.write(test_agents)

# tests/test_crd.py
test_crd = '''"""
Tests unitaires avancés pour le CRD

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from core.grondona_crd import GrondonaCRD, simulate_crd


class TestCRDAdvanced:
    """Tests avancés pour le CRD"""
    
    def test_entropy_bound(self):
        crd = GrondonaCRD()
        crd.add_commodity("A", floor_price=10, ceiling_price=20, initial_price=15, initial_stock=100)
        crd.add_commodity("B", floor_price=5, ceiling_price=15, initial_price=10, initial_stock=200)
        
        entropy = crd.get_entropy_bound()
        assert entropy >= 0
    
    def test_total_stock_value(self):
        crd = GrondonaCRD()
        crd.add_commodity("A", floor_price=10, ceiling_price=20, initial_price=15, initial_stock=100)
        
        value = crd.total_stock_value()
        assert value == 1500  # 100 * 15
    
    def test_money_supply_never_negative(self):
        crd = GrondonaCRD()
        crd.add_commodity("A", floor_price=10, ceiling_price=20, initial_price=15, initial_stock=1000)
        
        for _ in range(100):
            price = 15 + np.random.normal(0, 5)
            price = max(1, price)
            crd.step({"A": price})
        
        assert crd.money_supply >= 0
    
    def test_simulation_stability(self):
        initial_prices = {"A": 100, "B": 50, "C": 25}
        results = simulate_crd(initial_prices, periods=200, price_volatility=0.3)
        
        money_supplies = [r["money_supply"] for r in results]
        assert all(m >= 0 for m in money_supplies)
'''

with open("/mnt/agents/output/yusuf-grondona-system/tests/test_crd.py", "w") as f:
    f.write(test_crd)

# tests/test_entropy.py
test_entropy = '''"""
Tests unitaires pour l'entropie

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import pytest
import numpy as np
from core.entropy_physical import PhysicalEntropy
from core.entropy_shannon import ShannonEntropy


class TestPhysicalEntropy:
    """Tests pour l'entropie physique"""
    
    def test_production_entropy_positive(self):
        entropy = PhysicalEntropy()
        result = entropy.production_entropy(10)
        assert result > 0
    
    def test_negentropy_capture(self):
        entropy = PhysicalEntropy()
        result = entropy.negentropy_capture(5, gamma=0.8)
        assert result == 4.0
    
    def test_critical_interest_rate(self):
        entropy = PhysicalEntropy()
        rate = entropy.find_critical_interest_rate(
            debt=100, low_entropy_extraction=10
        )
        assert 0 < rate < 0.1
        
        # Verify at critical rate, lambda ≈ 1
        lambda_val = entropy.bifurcation_parameter(100, rate, 10)
        assert abs(lambda_val - 1.0) < 0.001


class TestShannonEntropy:
    """Tests pour l'entropie de Shannon"""
    
    def test_price_entropy_uniform(self):
        prices = [10, 10, 10, 10]
        entropy = ShannonEntropy.price_entropy(prices)
        assert entropy >= 0
    
    def test_price_entropy_diverse(self):
        prices = [10, 20, 30, 40, 50]
        entropy = ShannonEntropy.price_entropy(prices)
        assert entropy > 0
    
    def test_transaction_entropy(self):
        transactions = [100, 200, 300, 400]
        entropy = ShannonEntropy.transaction_entropy(transactions)
        assert entropy > 0
    
    def test_empty_list(self):
        assert ShannonEntropy.price_entropy([]) == 0.0
        assert ShannonEntropy.transaction_entropy([]) == 0.0
'''

with open("/mnt/agents/output/yusuf-grondona-system/tests/test_entropy.py", "w") as f:
    f.write(test_entropy)

print("4 fichiers de tests créés: test_core.py, test_agents.py, test_crd.py, test_entropy.py")