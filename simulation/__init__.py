
# simulation/__init__.py
open("/mnt/agents/output/yusuf-grondona-system/simulation/__init__.py", "w").close()

# simulation/agents.py
agents_py = '''"""
Module d'agents pour la simulation multi-agents (Mesa)
Agents: ménages, banques, neurocognitifs

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from typing import Dict, List, Optional


class HouseholdAgent(Agent):
    """Agent ménage avec productivité hétérogène"""
    
    def __init__(self, unique_id, model, 
                 productivity: float,
                 initial_wealth: float,
                 propensity_save: float):
        super().__init__(unique_id, model)
        self.productivity = productivity
        self.wealth = initial_wealth
        self.propensity_save = propensity_save
        self.consumption = 0
        self.default = False
        self.capital = initial_wealth * 0.3
        self.debt = 0.0
        self.history = []
    
    def produce(self) -> float:
        """Production = productivité * capital^β"""
        beta = 0.3
        output = self.productivity * (self.capital ** beta)
        self.wealth += output
        return output
    
    def consume_and_save(self) -> float:
        """Consommation = (1 - propension à épargner) * richesse"""
        self.consumption = (1 - self.propensity_save) * self.wealth
        if self.consumption > self.wealth:
            self.consumption = self.wealth
        self.wealth -= self.consumption
        return self.consumption
    
    def invest(self, amount: float) -> None:
        """Investit dans le capital"""
        if amount <= self.wealth:
            self.wealth -= amount
            self.capital += amount
    
    def borrow(self, amount: float, interest_rate: float) -> bool:
        """Emprunte avec intérêt"""
        if self.debt < self.wealth * 2:
            self.debt += amount
            self.wealth += amount
            return True
        return False
    
    def service_debt(self) -> float:
        """Sert la dette (paiement des intérêts)"""
        interest = self.debt * 0.05
        if self.wealth >= interest:
            self.wealth -= interest
            return interest
        else:
            self.default = True
            return 0.0
    
    def pay_zakat(self, rate: float = 0.025, nisab: float = 100) -> float:
        """Paye la zakat sur la richesse"""
        if self.wealth > nisab:
            zakat = (self.wealth - nisab) * rate
            self.wealth -= zakat
            return zakat
        return 0.0
    
    def mudaraba_invest(self, capital: float, 
                        profit_share_ratio: float = 0.7,
                        risk_factor: float = 0.05) -> float:
        """Contrat de mudaraba (profit-sharing)"""
        if capital > self.wealth:
            return 0.0
        
        self.wealth -= capital
        
        if np.random.rand() < risk_factor:
            loss = capital * np.random.uniform(0, 0.5)
            self.wealth -= loss
            return -loss
        
        profit = capital * (self.productivity ** 0.5) * np.random.uniform(0.9, 1.1)
        investor_share = profit * profit_share_ratio
        entrepreneur_share = profit * (1 - profit_share_ratio)
        
        self.wealth += entrepreneur_share
        return investor_share
    
    def step(self) -> None:
        """Étape de l'agent"""
        self.produce()
        
        if self.debt > 0:
            self.service_debt()
        
        self.consume_and_save()
        
        invest_amount = self.wealth * 0.1
        if invest_amount > 0:
            self.invest(invest_amount)
        
        self.history.append({
            'wealth': self.wealth,
            'capital': self.capital,
            'debt': self.debt,
            'consumption': self.consumption,
            'default': self.default
        })


class FinancialAgent(Agent):
    """Agent financier (banque)"""
    
    def __init__(self, unique_id, model, 
                 reserves: float = 1000,
                 reserve_ratio: float = 0.1):
        super().__init__(unique_id, model)
        self.reserves = reserves
        self.reserve_ratio = reserve_ratio
        self.loans = 0.0
        self.deposits = 0.0
        self.interest_rate = 0.05
    
    def create_money(self, amount: float) -> float:
        """Crée de la monnaie par le crédit (réserves fractionnaires)"""
        max_credit = self.reserves / self.reserve_ratio - self.loans
        if max_credit < 0:
            max_credit = 0
        
        credit = min(amount, max_credit)
        if credit > 0:
            self.loans += credit
            self.deposits += credit
            return credit
        return 0.0
    
    def collect_interest(self) -> float:
        """Collecte les intérêts sur les prêts"""
        interest = self.loans * self.interest_rate
        self.reserves += interest
        return interest
    
    def step(self) -> None:
        self.collect_interest()


class MonetaryModel(Model):
    """Modèle principal avec agents"""
    
    def __init__(self, n_agents: int = 100, regime: str = "fiat"):
        super().__init__()
        self.n_agents = n_agents
        self.regime = regime
        self.schedule = RandomActivation(self)
        
        productivity_dist = np.random.lognormal(mean=0, sigma=0.5, size=n_agents)
        wealth_dist = np.random.uniform(10, 1000, size=n_agents)
        propensity_dist = np.random.beta(a=2, b=5, size=n_agents)
        
        for i in range(n_agents):
            agent = HouseholdAgent(
                i, self,
                productivity=productivity_dist[i],
                initial_wealth=wealth_dist[i],
                propensity_save=propensity_dist[i]
            )
            self.schedule.add(agent)
        
        self.bank = FinancialAgent(n_agents + 1, self)
        self.schedule.add(self.bank)
        
        self.datacollector = DataCollector(
            model_reporters={
                "GDP": self.compute_gdp,
                "Gini": self.compute_gini,
                "DefaultRate": self.compute_default_rate,
                "WealthInequality": self.compute_wealth_inequality,
                "Entropy": self.compute_entropy,
                "TotalDebt": self.compute_total_debt
            },
            agent_reporters={
                "Wealth": "wealth",
                "Debt": "debt",
                "Default": "default"
            }
        )
        
        self.step_count = 0
    
    def compute_gdp(self) -> float:
        """PIB = somme des consommations"""
        return sum(
            a.consumption for a in self.schedule.agents 
            if isinstance(a, HouseholdAgent)
        )
    
    def compute_gini(self) -> float:
        """Coefficient de Gini"""
        wealths = [a.wealth for a in self.schedule.agents if isinstance(a, HouseholdAgent)]
        wealths_sorted = np.sort(wealths)
        n = len(wealths_sorted)
        if n == 0:
            return 1.0
        cum_wealth = np.cumsum(wealths_sorted) / np.sum(wealths_sorted)
        gini = 1 - 2 * np.sum(cum_wealth[:-1] + 1/(2*n)) / n
        return gini
    
    def compute_default_rate(self) -> float:
        """Taux de défaut"""
        n_default = sum(1 for a in self.schedule.agents 
                       if isinstance(a, HouseholdAgent) and a.default)
        n_agents = sum(1 for a in self.schedule.agents if isinstance(a, HouseholdAgent))
        return n_default / n_agents if n_agents > 0 else 0.0
    
    def compute_wealth_inequality(self) -> float:
        """Part du top 10%"""
        wealths = [a.wealth for a in self.schedule.agents if isinstance(a, HouseholdAgent)]
        wealths_sorted = np.sort(wealths)[::-1]
        top10 = np.sum(wealths_sorted[:len(wealths_sorted)//10])
        return top10 / np.sum(wealths_sorted) if np.sum(wealths_sorted) > 0 else 0.0
    
    def compute_entropy(self, alpha: float = 0.5) -> float:
        """Entropie monétaire"""
        wealths = [a.wealth for a in self.schedule.agents if isinstance(a, HouseholdAgent)]
        consumptions = [a.consumption for a in self.schedule.agents if isinstance(a, HouseholdAgent)]
        
        if np.mean(wealths) > 0:
            h_info = np.var(wealths) / (np.mean(wealths) ** 2)
        else:
            h_info = 1.0
        
        if np.mean(consumptions) > 0:
            h_real = np.var(consumptions) / (np.mean(consumptions) ** 2)
        else:
            h_real = 1.0
        
        return alpha * h_info + (1-alpha) * h_real
    
    def compute_total_debt(self) -> float:
        """Dette totale"""
        return sum(a.debt for a in self.schedule.agents if isinstance(a, HouseholdAgent))
    
    def step(self, shock_intensity: float = 0) -> None:
        """Une étape de simulation"""
        if shock_intensity > 0:
            for a in self.schedule.agents:
                if isinstance(a, HouseholdAgent):
                    a.wealth *= (1 - shock_intensity)
        
        if "islamic" in self.regime.lower():
            for a in self.schedule.agents:
                if isinstance(a, HouseholdAgent):
                    a.pay_zakat()
        
        if "no_interest" in self.regime.lower():
            self.bank.interest_rate = 0.0
        
        self.schedule.step()
        self.datacollector.collect(self)
        self.step_count += 1
    
    def run_simulation(self, steps: int = 500) -> object:
        """Lance la simulation"""
        for _ in range(steps):
            self.step()
        return self.datacollector.get_model_vars_dataframe()
'''

with open("/mnt/agents/output/yusuf-grondona-system/simulation/agents.py", "w") as f:
    f.write(agents_py)

print("simulation/agents.py créé")