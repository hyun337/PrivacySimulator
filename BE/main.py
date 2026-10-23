"""
개인정보 노출 시뮬레이터 - Flask 백엔드 (간소화 버전)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from inference_rules import PrivacyInferenceEngine
from risk_calculator import RiskCalculator

app = Flask(__name__)
CORS(app)

# 데이터 로드
def load_users():
    try:
        if os.path.exists('virtual_users.json'):
            with open('virtual_users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)
            # dict 형태면 simulation_users 키로 접근
            if isinstance(users, dict):
                users = users.get('simulation_users', [])
            print(f"[OK] {len(users)} users loaded")
            return users
    except Exception as e:
        print(f"[ERROR] Data load failed: {e}")
    return []

VIRTUAL_USERS = load_users()
inference_engine = PrivacyInferenceEngine()
risk_calculator = RiskCalculator()


@app.route("/", methods=["GET"])
def home():
    """API 상태"""
    return jsonify({
        "status": "running",
        "version": "1.0",
        "total_users": len(VIRTUAL_USERS),
        "endpoints": {
            "users": "GET /api/users",
            "user_detail": "GET /api/user/<id>",
            "analyze": "POST /api/analyze",
            "stats": "GET /api/statistics"
        }
    })


@app.route("/api/users", methods=["GET"])
def get_users():
    """사용자 목록 (페이지네이션)"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    start = (page - 1) * per_page
    end = start + per_page
    
    users_page = VIRTUAL_USERS[start:end]
    
    return jsonify({
        "total": len(VIRTUAL_USERS),
        "page": page,
        "per_page": per_page,
        "users": [{
            "user_id": u.get("user_id"),
            "persona": u.get("persona"),
            "age": u.get("demographics", {}).get("age")
        } for u in users_page]
    })


@app.route("/api/user/<user_id>", methods=["GET"])
def get_user_detail(user_id):
    """사용자 상세"""
    user = next((u for u in VIRTUAL_USERS if u.get("user_id") == user_id), None)
    return jsonify(user) if user else (jsonify({"error": "Not found"}), 404)


@app.route("/api/analyze", methods=["POST"])
def analyze_user():
    """사용자 분석"""
    data = request.json
    if not data or "user_id" not in data:
        return jsonify({"error": "user_id required"}), 400
    
    user = next((u for u in VIRTUAL_USERS if u.get("user_id") == data["user_id"]), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # 1. 추론 및 위험도 계산
        inference = inference_engine.infer_all(user)
        score, level, breakdown = risk_calculator.calculate(user, inference)
        
        # 2. 결과 반환 (여기에 data_fragments를 추가해서 원본 데이터를 프론트로 보냅니다!)
        return jsonify({
            "user_id": user.get("user_id"),
            "persona": user.get("persona"),
            "inference_results": inference,
            "risk_assessment": {
                "score": score,
                "level": level,
                "breakdown": breakdown
            },
            "recommendations": generate_recommendations(level, inference),
            # --- 이 아랫부분이 추가되어야 프론트엔드 표가 채워집니다 ---
            "data_fragments": user.get("data_fragments", {}) 
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """전체 통계"""
    personas = {}
    for u in VIRTUAL_USERS:
        p = u.get("persona", "unknown")
        personas[p] = personas.get(p, 0) + 1
    
    return jsonify({
        "total": len(VIRTUAL_USERS),
        "persona_distribution": personas
    })


def generate_recommendations(level, inference):
    """권장사항 생성"""
    recs = []
    
    if level in ["High", "Critical"]:
        recs.append("[!] Location sharing settings should be restricted")
        recs.append("[!] Minimize SNS account linkage")
    elif level == "Medium":
        recs.append("[*] Periodically review personal information disclosure scope")
    else:
        recs.append("[OK] Current protection level is good")
    
    if inference.get("residence_inferred"):
        recs.append("[!] Residence inferred: Limit location sharing during late night hours")
    
    if inference.get("workplace_inferred"):
        recs.append("[!] Workplace inferred: Avoid weekday morning check-ins")
    
    return recs


if __name__ == "__main__":
    print("=" * 60)
    print("Privacy Exposure Simulator Backend")
    print("=" * 60)
    print(f"Users: {len(VIRTUAL_USERS)}")
    print(f"Address: http://localhost:5001")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
