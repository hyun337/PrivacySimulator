from typing import Dict, List
from collections import Counter

class PrivacyInferenceEngine:
    """파편화된 데이터를 결합하여 민감한 정보를 추론"""
    
    def __init__(self):
        self.min_evidence = 5  # 추론에 필요한 최소 증거 수
        self.confidence_threshold = 0.7  # 추론 확신 임계값
    
    def infer_all(self, user_data: Dict) -> Dict:
        """전체 추론 실행"""
        results = {
            "residence_inferred": False,
            "workplace_inferred": False,
            "lifestyle_pattern_inferred": False,
            "economic_level_inferred": False,
            "family_structure_inferred": False,
            "inferred_details": {},
            "confidence_scores": {}, # 여기에 각 항목별 신뢰도 저장
            "critical_inferences": [],
            "data_combinations": []
        }
        
        data = user_data.get("data_fragments", {})
        
        # 각 추론 실행
        self._infer_residence(data, results)
        self._infer_workplace(data, results)
        self._infer_lifestyle(data, results)
        self._infer_economic(data, results)
        self._infer_family(data, results)
        
        # 데이터 결합 분석
        results["data_combinations"] = self._analyze_combinations(results)
        
        return results
    
    def _infer_residence(self, data: Dict, results: Dict):
        """주거지 추론"""
        locations = data.get("location_history", [])
        if len(locations) < self.min_evidence: return
        
        night_locs = [loc for loc in locations if loc.get("pattern") == "nightly" and loc.get("type") == "residence"]
        if len(night_locs) < self.min_evidence: return
        
        areas = [loc.get("area", "unknown") for loc in night_locs]
        area_counts = Counter(areas)
        most_common, count = area_counts.most_common(1)[0]
        
        confidence = min((count / 10) * 0.2 + 0.5, 1.0) # 증거가 많을수록 신뢰도 상승
        
        if confidence >= self.confidence_threshold:
            results["residence_inferred"] = True
            results["confidence_scores"]["residence"] = round(confidence, 2)
            results["inferred_details"]["residence"] = {
                "area": most_common,
                "district": night_locs[0].get("district", "알 수 없음"),
                "evidence_count": count
            }
            results["critical_inferences"].append({"type": "residence", "severity": "high", "description": f"주거지: {most_common}"})

    def _infer_workplace(self, data: Dict, results: Dict):
        """직장 위치 추론"""
        locations = data.get("location_history", [])
        work_locs = [loc for loc in locations if loc.get("pattern") == "weekday_morning" and loc.get("type") == "work"]
        if len(work_locs) < self.min_evidence: return
        
        areas = [loc.get("area", "unknown") for loc in work_locs]
        most_common, count = Counter(areas).most_common(1)[0]
        confidence = min((count / 10) * 0.2 + 0.5, 1.0)
        
        results["workplace_inferred"] = True
        results["confidence_scores"]["workplace"] = round(confidence, 2)
        results["inferred_details"]["workplace"] = {"area": most_common, "evidence_count": count}

    def _infer_lifestyle(self, data: Dict, results: Dict):
        """생활 패턴 추론"""
        sns = data.get("sns_activities", [])
        if len(sns) < 3: return
        
        patterns = [act.get("time_pattern", "unknown") for act in sns]
        dominant = Counter(patterns).most_common(1)[0][0]
        
        # SNS 활동량이 많을수록 신뢰도 보정
        confidence = min(0.6 + (len(sns) * 0.01), 0.95)
        
        results["lifestyle_pattern_inferred"] = True
        results["confidence_scores"]["lifestyle"] = round(confidence, 2)
        results["inferred_details"]["lifestyle"] = {"dominant_time": dominant, "activity_level": "높음" if len(sns) >= 30 else "보통"}

    def _infer_economic(self, data: Dict, results: Dict):
        """경제적 수준 추론"""
        photos = data.get("photo_metadata", [])
        if len(photos) < 3: return
        
        all_indicators = []
        for photo in photos:
            all_indicators.extend(photo.get("economic_indicators", []))
            all_indicators.extend(photo.get("detected_objects", []))
        
        luxury_keywords = ["luxury", "designer", "premium", "high", "expensive"]
        luxury_count = sum(1 for ind in all_indicators if any(kw in str(ind).lower() for kw in luxury_keywords))
        
        level = "상위권" if luxury_count >= 3 else "일반"
        confidence = min(0.5 + (luxury_count * 0.1), 0.9)
        
        results["economic_level_inferred"] = True
        results["confidence_scores"]["economic"] = round(confidence, 2)
        results["inferred_details"]["economic"] = {"level": level, "luxury_indicators": luxury_count}

    def _infer_family(self, data: Dict, results: Dict):
        """가구 구성 추론"""
        photos = data.get("photo_metadata", [])
        sns = data.get("sns_activities", [])
        
        family_evidence = 0
        for photo in photos:
            family_evidence += sum(1 for o in photo.get("detected_objects", []) if any(kw in str(o).lower() for kw in ["child", "kid", "baby", "toy"]))
        for act in sns:
            family_evidence += sum(1 for t in act.get("hashtags", []) if any(kw in t for kw in ["육아", "맘", "아이", "자녀"]))
            
        if family_evidence >= 2:
            confidence = min(0.6 + (family_evidence * 0.05), 0.95)
            results["family_structure_inferred"] = True
            results["confidence_scores"]["family"] = round(confidence, 2)
            results["inferred_details"]["family"] = {"description": "자녀가 있는 가정", "evidence": family_evidence}

    def _analyze_combinations(self, results: Dict) -> List[Dict]:
        """데이터 결합 패턴 분석"""
        combos = []
        if results["residence_inferred"] and results["workplace_inferred"]:
            combos.append({"type": "location_exposure", "multiplier": 1.5})
        if results["residence_inferred"] and results["lifestyle_pattern_inferred"]:
            combos.append({"type": "real_time_tracking", "multiplier": 1.3})
        return combos
