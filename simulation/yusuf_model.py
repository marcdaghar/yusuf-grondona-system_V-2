
# simulation/yusuf_model.py
yusuf_model = '''"""
Yusuf Counter-Cycle Model — Simulation Yusuf vs Capitaliste
Règle contra-cyclique (Coran 12:47-48) vs système capitaliste (dette à intérêt)

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any


@dataclass
class YusufConfig:
    """Configuration du modèle contre-cyclique de Yusuf"""
    
    T: float = 100.0              # Durée simulation (années)
    dt: float = 0.1               # Pas de temps (années)
    
    need: float = 0.7             # Besoin de consommation minimum/an
    P_mean: float = 1.0           # Production moyenne
    P_amplitude: float = 0.5      # Amplitude du cycle
    period: float = 14.0          # Période du cycle (7+7 = 14 ans)
    
    interest_rate: float = 0.05   # Taux d'intérêt (système capitaliste)
    
    stock_initial: float = 0.5    # Stock initial (années de consommation)
    threshold_factor: float = 0.3 # Facteur pour les seuils
    
    gamification_enabled: bool = True
    compliance_threshold: float = 0.8
    penalty_rate: float = 0.3
    reward_rate: float = 0.1
    
    noise_amplitude: float = 0.03 # Bruit de production
    
    @property
    def P_bar(self) -> float:
        """Seuil d'abondance"""
        return self.P_mean + self.P_amplitude * self.threshold_factor
    
    @property
    def P_underline(self) -> float:
        """Seuil de rareté"""
        return self.P_mean - self.P_amplitude * self.threshold_factor
    
    @property
    def n_steps(self) -> int:
        return int(self.T / self.dt)


@dataclass
class SimulationResult:
    """Résultats d'une simulation"""
    t: np.ndarray
    P: np.ndarray
    S: np.ndarray
    C: np.ndarray
    compliance: Optional[np.ndarray] = None
    config: Optional[YusufConfig] = None
    system_name: str = ""
    crisis_detected: bool = False
    
    @property
    def coverage_ratio(self) -> np.ndarray:
        return self.S / (self.config.need if self.config else 0.7)
    
    @property
    def final_stock(self) -> float:
        return self.S[-1] if len(self.S) > 0 else 0.0
    
    @property
    def mean_consumption(self) -> float:
        return float(np.mean(self.C))
    
    @property
    def consumption_volatility(self) -> float:
        return float(np.std(self.C))
    
    @property
    def solvency_rate(self) -> float:
        return float(np.sum(self.S > 0) / len(self.S) * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_name": self.system_name,
            "final_stock": self.final_stock,
            "mean_consumption": self.mean_consumption,
            "consumption_volatility": self.consumption_volatility,
            "solvency_rate": self.solvency_rate,
            "crisis_detected": self.crisis_detected
        }


class YusufSystem:
    """
    Système contre-cyclique de Yusuf
    
    Règle:
    - Abondance (P > P_bar) : Minimiser consommation, stocker le surplus
    - Rareté (P < P_underline) : Déstocker pour maintenir consommation
    - Équilibre : Consommation = production
    """
    
    def __init__(self, config: YusufConfig):
        self.config = config
        self.reset()
    
    def reset(self) -> None:
        self.S = np.zeros(self.config.n_steps)
        self.C = np.zeros(self.config.n_steps)
        self.S[0] = self.config.stock_initial
        self.compliance = np.zeros(self.config.n_steps) if self.config.gamification_enabled else None
    
    def _compute_production(self) -> np.ndarray:
        t = np.linspace(0, self.config.T, self.config.n_steps)
        P = self.config.P_mean + self.config.P_amplitude * np.sin(2 * np.pi * t / self.config.period)
        
        if self.config.noise_amplitude > 0:
            noise = np.random.normal(0, self.config.noise_amplitude, len(t))
            P = P + noise
        
        return np.maximum(P, 0.1)
    
    def _update_compliance(self, idx: int, behavior_correct: bool) -> float:
        if not self.config.gamification_enabled:
            return 0.0
        
        if idx == 0:
            score = 1.0
        else:
            score = self.compliance[idx - 1]
        
        if behavior_correct:
            score = min(1.0, score + self.config.reward_rate * self.config.dt)
        else:
            score = max(0.0, score - self.config.penalty_rate * self.config.dt)
        
        return score
    
    def _get_effective_need(self, score: float) -> float:
        if not self.config.gamification_enabled:
            return self.config.need
        
        if score >= self.config.compliance_threshold:
            return self.config.need * (1 - self.config.reward_rate)
        else:
            return self.config.need * (1 + self.config.penalty_rate)
    
    def run(self) -> SimulationResult:
        self.reset()
        
        P = self._compute_production()
        t = np.linspace(0, self.config.T, self.config.n_steps)
        
        P_bar = self.config.P_bar
        P_underline = self.config.P_underline
        crisis_detected = False
        
        for i in range(1, self.config.n_steps):
            production = P[i]
            stock_prev = self.S[i-1]
            score_prev = self.compliance[i-1] if self.compliance is not None else 1.0
            
            effective_need = self._get_effective_need(score_prev)
            
            if production > P_bar:
                # ABONDANCE : stocker
                self.C[i] = min(production, effective_need)
                dS = (production - self.C[i]) * self.config.dt
                self.S[i] = stock_prev + dS
                behavior_correct = (self.C[i] <= effective_need + 0.1)
            
            elif production < P_underline:
                # RARETÉ : déstocker
                needed_from_stock = max(0, effective_need - production)
                max_withdraw = stock_prev / self.config.dt if self.config.dt > 0 else 0
                withdraw = min(needed_from_stock, max_withdraw)
                self.C[i] = production + withdraw
                dS = (production - self.C[i]) * self.config.dt
                self.S[i] = stock_prev + dS
                behavior_correct = (withdraw <= stock_prev + 1e-6)
            
            else:
                # ÉQUILIBRE
                self.C[i] = production
                self.S[i] = stock_prev
                behavior_correct = True
            
            if self.S[i] < 0:
                self.S[i] = 0
                crisis_detected = True
            
            if self.compliance is not None:
                self.compliance[i] = self._update_compliance(i, behavior_correct)
        
        return SimulationResult(
            t=t, P=P, S=self.S, C=self.C,
            compliance=self.compliance, config=self.config,
            system_name="Yusuf (counter-cycle)",
            crisis_detected=crisis_detected
        )


class CapitalistSystem:
    """Système capitaliste de référence avec intérêts composés"""
    
    def __init__(self, config: YusufConfig):
        self.config = config
        self.reset()
    
    def reset(self) -> None:
        self.S = np.zeros(self.config.n_steps)
        self.C = np.zeros(self.config.n_steps)
        self.D = np.zeros(self.config.n_steps)
        self.S[0] = self.config.stock_initial
        self.D[0] = 0.5
    
    def _compute_production(self) -> np.ndarray:
        t = np.linspace(0, self.config.T, self.config.n_steps)
        P = self.config.P_mean + self.config.P_amplitude * np.sin(2 * np.pi * t / self.config.period)
        if self.config.noise_amplitude > 0:
            noise = np.random.normal(0, self.config.noise_amplitude, len(t))
            P = P + noise
        return np.maximum(P, 0.1)
    
    def run(self) -> SimulationResult:
        self.reset()
        
        P = self._compute_production()
        t = np.linspace(0, self.config.T, self.config.n_steps)
        crisis_detected = False
        
        for i in range(1, self.config.n_steps):
            dt = self.config.dt
            
            self.D[i] = self.D[i-1] * (1 + self.config.interest_rate * dt)
            debt_service = self.D[i-1] * self.config.interest_rate * dt
            
            available = P[i] - debt_service
            self.C[i] = min(available, self.config.need)
            
            dS = (P[i] - self.C[i]) * dt - debt_service
            self.S[i] = max(0, self.S[i-1] + dS)
            
            if self.S[i] == 0 and self.S[i-1] > 0:
                crisis_detected = True
        
        return SimulationResult(
            t=t, P=P, S=self.S, C=self.C,
            config=self.config, system_name="Capitalist (debt, interest)",
            crisis_detected=crisis_detected
        )


class ScenarioComparator:
    """Compare les systèmes Yusuf et Capitaliste"""
    
    def __init__(self, config: YusufConfig = None):
        self.config = config or YusufConfig()
    
    def run_single(self) -> Tuple[SimulationResult, SimulationResult]:
        """Exécute une comparaison unique"""
        np.random.seed(42)
        yusuf = YusufSystem(self.config)
        capitalist = CapitalistSystem(self.config)
        return yusuf.run(), capitalist.run()
    
    def run_monte_carlo(self, n_simulations: int = 100) -> Dict[str, Any]:
        """Exécute des simulations Monte Carlo"""
        yusuf_metrics = []
        capitalist_metrics = []
        
        for seed in range(n_simulations):
            np.random.seed(seed)
            yusuf = YusufSystem(self.config)
            capitalist = CapitalistSystem(self.config)
            y_res = yusuf.run()
            c_res = capitalist.run()
            yusuf_metrics.append(y_res.to_dict())
            capitalist_metrics.append(c_res.to_dict())
        
        def aggregate(metrics_list):
            return {
                "final_stock_mean": np.mean([m["final_stock"] for m in metrics_list]),
                "final_stock_std": np.std([m["final_stock"] for m in metrics_list]),
                "solvency_rate_mean": np.mean([m["solvency_rate"] for m in metrics_list]),
                "consumption_volatility_mean": np.mean([m["consumption_volatility"] for m in metrics_list])
            }
        
        return {
            "yusuf": aggregate(yusuf_metrics),
            "capitalist": aggregate(capitalist_metrics),
            "n_simulations": n_simulations
        }


if __name__ == "__main__":
    config = YusufConfig(T=50, dt=0.5)
    comparator = ScenarioComparator(config)
    y_res, c_res = comparator.run_single()
    
    print("=" * 60)
    print("YUSUF COUNTER-CYCLE MODEL")
    print("=" * 60)
    print(f"Yusuf final stock    : {y_res.final_stock:.2f}")
    print(f"Capitalist final stock: {c_res.final_stock:.2f}")
    print(f"Yusuf solvency       : {y_res.solvency_rate:.1f}%")
    print(f"Capitalist solvency   : {c_res.solvency_rate:.1f}%")
'''

with open("/mnt/agents/output/yusuf-grondona-system/simulation/yusuf_model.py", "w") as f:
    f.write(yusuf_model)

print("simulation/yusuf_model.py créé")