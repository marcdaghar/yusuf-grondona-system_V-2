
# ai/muhtassib_ai.py
muhtassib_ai = '''"""
Module d'IA assistante pour le muhtassib
Détection d'anomalies et signaux faibles

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional


class MuhtassibAI:
    """
    Intelligence artificielle assistante pour le muhtassib
    - Détection d'anomalies (Isolation Forest)
    - Détection de signaux faibles
    - Coordination logistique
    """
    
    def __init__(self, contamination: float = 0.1):
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.anomaly_threshold = -0.5
    
    def fit(self, data: np.ndarray) -> None:
        """Entraîne le modèle sur des données historiques"""
        scaled_data = self.scaler.fit_transform(data)
        self.isolation_forest.fit(scaled_data)
        self.is_fitted = True
    
    def detect_anomalies(self, data: np.ndarray) -> Tuple[np.ndarray, List[int]]:
        """
        Détecte les anomalies dans les données
        
        Returns:
            (scores, indices_anomalies)
        """
        if not self.is_fitted:
            return np.array([]), []
        
        scaled_data = self.scaler.transform(data)
        scores = self.isolation_forest.decision_function(scaled_data)
        anomalies = np.where(scores < self.anomaly_threshold)[0]
        
        return scores, anomalies.tolist()
    
    def detect_market_anomalies(self, 
                                prices: Dict[str, float],
                                historical: Dict[str, List[float]]) -> Dict[str, bool]:
        """Détecte les anomalies de marché"""
        anomalies = {}
        
        for item, current_price in prices.items():
            if item not in historical:
                continue
            
            hist = historical[item]
            if len(hist) < 10:
                continue
            
            mean_price = np.mean(hist[-20:])
            std_price = np.std(hist[-20:])
            
            if std_price > 0:
                z_score = abs(current_price - mean_price) / std_price
                anomalies[item] = z_score > 3.0
            else:
                anomalies[item] = False
        
        return anomalies
    
    def detect_weak_signals(self, 
                           data: Dict,
                           thresholds: Dict[str, float]) -> Dict[str, float]:
        """Détecte les signaux faibles (prédictions de crise)"""
        signals = {}
        
        if 'volatility' in data:
            signals['stress_volatility'] = data['volatility'] / thresholds.get('volatility', 0.1)
        
        if 'debt_ratio' in data:
            signals['debt_stress'] = data['debt_ratio'] / thresholds.get('debt_ratio', 0.6)
        
        if 'inventory_level' in data:
            signals['inventory_stress'] = 1.0 - data['inventory_level'] / thresholds.get('inventory', 1.0)
        
        return signals
    
    def suggest_coordination(self, 
                            warehouse_stocks: Dict[str, float],
                            demand_forecast: Dict[str, float]) -> Dict[str, str]:
        """Suggère des actions de coordination logistique"""
        suggestions = {}
        
        for warehouse, stock in warehouse_stocks.items():
            if warehouse in demand_forecast:
                demand = demand_forecast[warehouse]
                if stock < demand * 1.2:
                    suggestions[warehouse] = f"Réapprovisionnement urgent (stock {stock:.0f}, demande {demand:.0f})"
                elif stock > demand * 3:
                    suggestions[warehouse] = f"Excédent de stock (réduire commandes)"
                else:
                    suggestions[warehouse] = "Niveau normal"
        
        return suggestions
    
    def alert_muhtassib(self, 
                       anomalies: List[str],
                       weak_signals: Dict[str, float],
                       threshold: float = 0.8) -> Dict[str, str]:
        """Génère des alertes pour le muhtassib"""
        alerts = {}
        
        for anomaly in anomalies:
            alerts[f"ANOMALIE_{anomaly}"] = "Critique"
        
        for signal, value in weak_signals.items():
            if value > threshold:
                alerts[f"SIGNAL_{signal}"] = f"Alerte (niveau {value:.2f})"
        
        return alerts
'''

with open("/mnt/agents/output/yusuf-grondona-system/ai/muhtassib_ai.py", "w") as f:
    f.write(muhtassib_ai)

# ai/early_warning.py
early_warning = '''"""
Système d'alerte précoce pour les crises

Author: Marc Daghar
License: CC BY-SA 4.0
"""

import numpy as np
from typing import Dict, List, Tuple


class EarlyWarningSystem:
    """Système d'alerte précoce basé sur les signaux faibles"""
    
    def __init__(self, warning_thresholds: Dict[str, float] = None):
        self.thresholds = warning_thresholds or {
            'lambda_bifurcation': 0.7,
            'gini_coefficient': 0.35,
            'trust_index': 0.75,
            'entropy_rate': 0.5,
            'default_rate': 0.1
        }
        self.history: List[Dict] = []
    
    def compute_risk_score(self, indicators: Dict[str, float]) -> float:
        """Calcule un score de risque global"""
        scores = []
        weights = {
            'lambda_bifurcation': 0.3,
            'gini_coefficient': 0.2,
            'trust_index': 0.2,
            'entropy_rate': 0.15,
            'default_rate': 0.15
        }
        
        for key, value in indicators.items():
            if key in self.thresholds:
                normalized = value / self.thresholds[key]
                scores.append(normalized * weights.get(key, 0.1))
        
        return sum(scores) / sum(weights.values()) if scores else 0.0
    
    def assess_crisis_probability(self, 
                                  current_state: Dict,
                                  historical_states: List[Dict]) -> float:
        """Évalue la probabilité de crise basée sur l'historique"""
        if len(historical_states) < 10:
            return 0.0
        
        current_score = self.compute_risk_score(current_state)
        historical_scores = [self.compute_risk_score(s) for s in historical_states]
        
        mean_score = np.mean(historical_scores)
        std_score = np.std(historical_scores)
        
        if std_score == 0:
            return 0.0
        
        z_score = (current_score - mean_score) / std_score
        probability = 1 / (1 + np.exp(-z_score))
        
        return probability
    
    def generate_alert(self, state: Dict) -> Dict:
        """Génère une alerte complète"""
        risk_score = self.compute_risk_score(state)
        
        alert_level = "NORMAL"
        if risk_score > 1.5:
            alert_level = "CRITIQUE"
        elif risk_score > 1.0:
            alert_level = "ÉLEVÉ"
        elif risk_score > 0.7:
            alert_level = "MODÉRÉ"
        
        triggered_indicators = {
            k: v for k, v in state.items()
            if k in self.thresholds and v > self.thresholds[k]
        }
        
        alert = {
            'timestamp': None,
            'risk_score': risk_score,
            'alert_level': alert_level,
            'triggered_indicators': triggered_indicators,
            'recommended_actions': self._recommend_actions(triggered_indicators)
        }
        
        self.history.append(alert)
        return alert
    
    def _recommend_actions(self, triggered: Dict[str, float]) -> List[str]:
        """Recommande des actions basées sur les indicateurs déclenchés"""
        actions = []
        
        if 'lambda_bifurcation' in triggered:
            actions.append("Réduire la dette agrégée ou augmenter l'extraction d'entropie basse")
        
        if 'gini_coefficient' in triggered:
            actions.append("Activer le mécanisme de redistribution Zakat")
        
        if 'trust_index' in triggered:
            actions.append("Renforcer la transparence du netting et des réserves")
        
        if 'entropy_rate' in triggered:
            actions.append("Optimiser la logistique pour réduire les pertes physiques")
        
        if 'default_rate' in triggered:
            actions.append("Activer le mécanisme de gel gradué du CRD")
        
        return actions
'''

with open("/mnt/agents/output/yusuf-grondona-system/ai/early_warning.py", "w") as f:
    f.write(early_warning)

print("ai/muhtassib_ai.py et ai/early_warning.py créés")