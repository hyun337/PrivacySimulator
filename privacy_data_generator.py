import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

class PrivacyDataGenerator:
    """개인정보 노출 시뮬레이터용 대량 가상 데이터 생성기"""
    
    def __init__(self, num_users=100):
        self.num_users = num_users
        self.personas = self._define_personas()
        self.locations = self._define_locations()
        
    def _define_personas(self) -> Dict:
        """사용자 페르소나 정의"""
        return {
            "office_worker": {
                "weight": 0.35,
                "age_range": (25, 40),
                "economic_level": ["medium", "high"],
                "hashtags": ["#회사생활", "#야근", "#퇴근", "#직장인", "#월요병", "#불금"]
            },
            "student": {
                "weight": 0.25,
                "age_range": (19, 26),
                "economic_level": ["low", "medium"],
                "hashtags": ["#대학생", "#과제", "#시험", "#도서관", "#팀플", "#공강"]
            },
            "freelancer": {
                "weight": 0.15,
                "age_range": (25, 45),
                "economic_level": ["medium", "high"],
                "hashtags": ["#프리랜서", "#재택", "#카페작업", "#노마드", "#부업"]
            },
            "parent": {
                "weight": 0.15,
                "age_range": (30, 50),
                "economic_level": ["medium", "high"],
                "hashtags": ["#육아", "#맘스타그램", "#아이와함께", "#유치원", "#초등맘"]
            },
            "business_owner": {
                "weight": 0.10,
                "age_range": (30, 55),
                "economic_level": ["high"],
                "hashtags": ["#사장님", "#자영업", "#창업", "#가게운영", "#소상공인"]
            }
        }
    
    def _define_locations(self) -> Dict:
        """서울 주요 지역 좌표"""
        return {
            "강남": {"lat": 37.4979, "lng": 127.0276, "district": "강남구"},
            "성수": {"lat": 37.5445, "lng": 127.0557, "district": "성동구"},
            "홍대": {"lat": 37.5563, "lng": 126.9223, "district": "마포구"},
            "신촌": {"lat": 37.5591, "lng": 126.9425, "district": "서대문구"},
            "잠실": {"lat": 37.5133, "lng": 127.1000, "district": "송파구"},
            "여의도": {"lat": 37.5219, "lng": 126.9245, "district": "영등포구"},
            "송파": {"lat": 37.5145, "lng": 127.1059, "district": "송파구"},
            "판교": {"lat": 37.3948, "lng": 127.1110, "district": "성남시"}
        }
    
    def generate_dataset(self) -> Dict:
        """전체 데이터셋 생성"""
        print("=" * 70)
        print("🔐 개인정보 노출 시뮬레이터 - 가상 데이터 생성 시작")
        print("=" * 70)
        print(f"생성할 사용자 수: {self.num_users}명\n")
        
        users = []
        for i in range(self.num_users):
            persona_type = self._select_weighted_persona()
            user = self._generate_user(f"U{i+1:03d}", persona_type)
            users.append(user)
            
            if (i + 1) % 10 == 0:
                print(f"✓ 진행: {i+1}/{self.num_users} ({(i+1)/self.num_users*100:.0f}%)")
        
        print("\n" + "=" * 70)
        print("✅ 데이터 생성 완료!")
        print("=" * 70)
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_users": len(users),
                "version": "1.0"
            },
            "simulation_users": users
        }
    
    def _select_weighted_persona(self) -> str:
        """가중치 기반 페르소나 선택"""
        personas = list(self.personas.keys())
        weights = [self.personas[p]["weight"] for p in personas]
        return random.choices(personas, weights=weights)[0]
    
    def _generate_user(self, user_id: str, persona_type: str) -> Dict:
        """개별 사용자 데이터 생성"""
        persona = self.personas[persona_type]
        age = random.randint(*persona["age_range"])
        economic = random.choice(persona["economic_level"])
        
        main_area = random.choice(list(self.locations.keys()))
        work_area = random.choice(list(self.locations.keys()))
        
        return {
            "user_id": user_id,
            "persona": persona_type,
            "demographics": {
                "age": age,
                "gender": random.choice(["male", "female"]),
                "economic_level": economic
            },
            "risk_level": 0,
            "data_fragments": {
                "location_history": self._generate_locations(persona_type, main_area, work_area),
                "sns_activities": self._generate_sns_activities(persona_type, persona),
                "profile_data": self._generate_profile(persona_type, age),
                "photo_metadata": self._generate_photos(economic)
            }
        }
    
    def _generate_locations(self, persona_type: str, main_area: str, work_area: str) -> List[Dict]:
        """위치 데이터 생성"""
        locations = []
        days = random.randint(30, 60)
        
        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            is_weekday = date.weekday() < 5
            
            # 직장인 패턴
            if persona_type == "office_worker" and is_weekday and random.random() < 0.9:
                locations.append(self._create_location(
                    date.replace(hour=random.randint(8, 9), minute=random.randint(0, 59)),
                    work_area, "work", "weekday_morning", 0.95
                ))
            
            # 밤 시간 주거지 (모든 페르소나)
            if random.random() < 0.85:
                locations.append(self._create_location(
                    date.replace(hour=random.randint(22, 23), minute=random.randint(0, 59)),
                    main_area, "residence", "nightly", 0.95
                ))
        
        return sorted(locations, key=lambda x: x["timestamp"], reverse=True)[:60]
    
    def _create_location(self, timestamp: datetime, area: str, 
                        loc_type: str, pattern: str, frequency: float) -> Dict:
        """개별 위치 기록"""
        coords = self.locations[area]
        return {
            "id": f"L{uuid.uuid4().hex[:8]}",
            "timestamp": timestamp.isoformat(),
            "coordinates": {
                "lat": round(coords["lat"] + random.uniform(-0.005, 0.005), 6),
                "lng": round(coords["lng"] + random.uniform(-0.005, 0.005), 6)
            },
            "area": area,
            "district": coords["district"],
            "type": loc_type,
            "pattern": pattern,
            "frequency_score": frequency
        }
    
    def _generate_sns_activities(self, persona_type: str, persona: Dict) -> List[Dict]:
        """SNS 활동 생성"""
        activities = []
        num_posts = random.randint(20, 40)
        hashtags_pool = persona["hashtags"]
        
        for _ in range(num_posts):
            days_ago = random.randint(0, 90)
            timestamp = datetime.now() - timedelta(days=days_ago)
            hour = random.randint(9, 23)
            timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))
            
            activities.append({
                "id": f"S{uuid.uuid4().hex[:8]}",
                "platform": random.choice(["instagram", "twitter", "facebook"]),
                "timestamp": timestamp.isoformat(),
                "hashtags": random.sample(hashtags_pool, min(3, len(hashtags_pool))),
                "time_pattern": self._classify_time_pattern(hour),
                "engagement_count": random.randint(5, 200)
            })
        
        return sorted(activities, key=lambda x: x["timestamp"], reverse=True)
    
    def _classify_time_pattern(self, hour: int) -> str:
        """시간대 분류"""
        if 6 <= hour < 9:
            return "morning"
        elif 12 <= hour < 14:
            return "lunch"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "late_night"
    
    def _generate_profile(self, persona_type: str, age: int) -> Dict:
        """프로필 데이터"""
        bios = {
            "office_worker": f"IT 기업 {random.randint(2, 10)}년차",
            "student": f"대학생 {random.randint(20, 25)}학번",
            "freelancer": f"프리랜서 디자이너",
            "parent": f"육아 중인 엄마",
            "business_owner": f"카페 운영 {random.randint(2, 10)}년차"
        }
        
        return {
            "bio": bios.get(persona_type, "일반 사용자"),
            "profile_image_analysis": {
                "background_type": random.choice(["office", "outdoor", "cafe", "home"]),
                "estimated_age": f"{age-2}-{age+2}"
            }
        }
    
    def _generate_photos(self, economic: str) -> List[Dict]:
        """사진 메타데이터"""
        photos = []
        num_photos = random.randint(10, 25)
        
        objects_by_economic = {
            "high": ["luxury_car", "designer_bag", "premium_electronics", "spacious_interior"],
            "medium": ["sedan", "branded_items", "standard_electronics", "apartment"],
            "low": ["public_transport", "budget_items", "basic_phone", "studio"]
        }
        
        for _ in range(num_photos):
            days_ago = random.randint(0, 90)
            upload_date = datetime.now() - timedelta(days=days_ago)
            
            photos.append({
                "id": f"P{uuid.uuid4().hex[:8]}",
                "upload_date": upload_date.strftime("%Y-%m-%d"),
                "detected_objects": random.sample(
                    objects_by_economic[economic], 
                    min(2, len(objects_by_economic[economic]))
                ),
                "scene_type": random.choice(["indoor", "outdoor", "cafe", "office", "home"]),
                "economic_indicators": [f"{economic}_lifestyle"]
            })
        
        return sorted(photos, key=lambda x: x["upload_date"], reverse=True)


def print_statistics(dataset: Dict):
    """통계 출력"""
    users = dataset['simulation_users']
    
    print(f"\n 총 사용자: {len(users)}명\n")
    
    # 페르소나별 통계
    persona_counts = {}
    for user in users:
        persona = user['persona']
        persona_counts[persona] = persona_counts.get(persona, 0) + 1
    
    print("👥 페르소나 분포:")
    for persona, count in sorted(persona_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {persona}: {count}명 ({count/len(users)*100:.1f}%)")
    
    # 데이터 포인트 집계
    total_locations = sum(len(u['data_fragments']['location_history']) for u in users)
    total_sns = sum(len(u['data_fragments']['sns_activities']) for u in users)
    total_photos = sum(len(u['data_fragments']['photo_metadata']) for u in users)
    
    print(f"\n 데이터 포인트:")
    print(f"  • 위치 기록: {total_locations:,}개")
    print(f"  • SNS 활동: {total_sns:,}개")
    print(f"  • 사진: {total_photos:,}개")
    print(f"  • 총합: {total_locations + total_sns + total_photos:,}개\n")


def main():
    """메인 실행"""
    print("\n" + "=" * 70)
    print("개인정보 노출 시뮬레이터 - 데이터 생성기")
    print("=" * 70)
    print("\n⚠️  이 데이터는 100% 가상이며 실제 개인과 무관합니다.\n")
    
    # 사용자 입력
    try:
        user_input = input("생성할 사용자 수를 입력하세요 (기본값: 100): ").strip()
        num_users = int(user_input) if user_input else 100
        
        if num_users < 10:
            print("⚠️  최소 10명 이상 입력해주세요.")
            return
        elif num_users > 500:
            confirm = input(f"⚠️  {num_users}명은 많은 양입니다. 계속하시겠습니까? (y/n): ")
            if confirm.lower() != 'y':
                print("취소되었습니다.")
                return
    except ValueError:
        print("❌ 잘못된 입력입니다. 기본값 100명으로 생성합니다.")
        num_users = 100
    
    # 데이터 생성
    generator = PrivacyDataGenerator(num_users=num_users)
    dataset = generator.generate_dataset()
    
    # 파일 저장
    output_file = f"privacy_simulator_data_{num_users}users.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    # 통계 출력
    print_statistics(dataset)
    
    print("=" * 70)
    print(f"✅ 파일 저장: {output_file}")
    print("=" * 70)
    print("\n다음 단계:")
    print(f"  cp {output_file} backend/virtual_users.json")
    print("  cd backend && python3 main.py\n")


if __name__ == "__main__":
    main()
