from typing import Dict, Tuple


class RiskCalculator:
    """개인정보 노출 위험도 계산 (0-100점)"""
    
    def __init__(self):
        # 가중치
        self.weights = {
            "residence": 30,
            "workplace": 25,
            "economic": 20,
            "lifestyle": 15,
            "family": 10
        }
        
        # 시너지 배수
        self.synergy = {
            "location_exposure": 1.5,
            "real_time_tracking": 1.3
        }
    
    def calculate(self, user_data: Dict, inference: Dict) -> Tuple[int, str, Dict]:
        """
        위험도 계산
        
        Returns:
            (점수, 등급, 상세정보)
        """
        # 1. 기본 점수 (가중치 기반)
        base = self._calc_base(inference)
        
        # 2. 신뢰도 조정
        adjusted = self._apply_confidence(inference)
        
        # 3. 시너지 보너스
        synergy = self._calc_synergy(inference)
        
        # 4. 노출 패널티
        penalty = self._calc_penalty(user_data)
        
        # 5. 최종 점수
        total = min(int(adjusted + synergy + penalty), 100)
        level = self._determine_level(total)
        
        breakdown = {
            "base_score": round(base, 1),
            "confidence_adjusted": round(adjusted, 1),
            "synergy_bonus": round(synergy, 1),
            "exposure_penalty": round(penalty, 1),
            "total_score": total
        }
        
        return total, level, breakdown
    
    def _calc_base(self, inference: Dict) -> float:
        """기본 점수"""
        score = 0.0
        if inference.get("residence_inferred"):
            score += self.weights["residence"]
        if inference.get("workplace_inferred"):
            score += self.weights["workplace"]
        if inference.get("economic_level_inferred"):
            score += self.weights["economic"]
        if inference.get("lifestyle_pattern_inferred"):
            score += self.weights["lifestyle"]
        if inference.get("family_structure_inferred"):
            score += self.weights["family"]
        return score
    
    def _apply_confidence(self, inference: Dict) -> float:
        """신뢰도 적용"""
        conf = inference.get("confidence_scores", {})
        score = 0.0
        
        for key, weight in self.weights.items():
            if key in conf:
                score += weight * conf[key]
        
        return score
    
    def _calc_synergy(self, inference: Dict) -> float:
        """시너지 보너스"""
        bonus = 0.0
        combos = inference.get("data_combinations", [])
        
        for combo in combos:
            combo_type = combo.get("type")
            multiplier = self.synergy.get(combo_type, 1.0)
            bonus += 10 * (multiplier - 1)
        
        # 4개 이상 추론 시 추가
        inferred = sum([
            inference.get("residence_inferred", False),
            inference.get("workplace_inferred", False),
            inference.get("economic_level_inferred", False),
            inference.get("lifestyle_pattern_inferred", False),
            inference.get("family_structure_inferred", False)
        ])
        
        if inferred >= 4:
            bonus += 15
        
        return bonus
    
    def _calc_penalty(self, user_data: Dict) -> float:
        """노출 패널티"""
        penalty = 0.0
        data = user_data.get("data_fragments", {})
        
        loc_count = len(data.get("location_history", []))
        if loc_count > 50:
            penalty += 10
        elif loc_count > 30:
            penalty += 5
        
        sns_count = len(data.get("sns_activities", []))
        if sns_count > 40:
            penalty += 8
        elif sns_count > 25:
            penalty += 4
        
        photo_count = len(data.get("photo_metadata", []))
        if photo_count > 25:
            penalty += 7
        elif photo_count > 15:
            penalty += 3
        
        return penalty
    
    def _determine_level(self, score: int) -> str:
        """등급 판정"""
        if score >= 70:
            return "Critical"
        elif score >= 50:
            return "High"
        elif score >= 30:
            return "Medium"
        else:
            return "Low"
