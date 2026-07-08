# 웰니스 웨어러블 사용자 인사이트 대시보드

웨어러블 기기의 활동·수면·심박·칼로리 데이터를 **마케팅팀(세분화·페르소나)** 과 **제품팀(기능별 행동 인사이트·참여 지속성)** 이 함께 참고하는 단일 페이지 대시보드입니다. 서버·빌드 없이 `index.html` 하나로 동작하며 GitHub Pages로 바로 배포할 수 있습니다.

## 라이브 미리보기 (로컬)

```bash
# 아무 정적 서버나 사용 (예시)
python3 -m http.server 8000
# 또는
npx serve .
# 브라우저에서 http://localhost:8000 접속
```

> `index.html`은 집계 데이터(`data/data_wellness.json` 내용)를 파일 안에 인라인으로 포함하고 있어, 서버 없이 파일을 더블클릭해도 열립니다. 폰트(Pretendard)와 차트(Chart.js)는 CDN에서 로드하므로 인터넷 연결이 필요합니다.

## 폴더 구조

```
wellness-dashboard/
├─ index.html                # 배포 대상 (자체 완결형 대시보드, 데이터 인라인)
├─ README.md
├─ .nojekyll                 # GitHub Pages의 Jekyll 처리 비활성화
├─ .gitignore
├─ docs/
│  └─ PRD.md                 # 제품 요구사항 정의서 (마케팅·제품팀용)
├─ scripts/
│  └─ aggregate.py           # 원본 CSV → data_wellness.json 집계 스크립트
└─ data/
   └─ data_wellness.json     # 대시보드가 사용하는 집계 데이터
```

## GitHub Pages 배포

1. 이 폴더를 새 GitHub 저장소로 push
2. GitHub 저장소 → **Settings → Pages**
3. **Source**: `Deploy from a branch` → 브랜치 `main`, 폴더 `/ (root)` 선택 후 Save
4. 1–2분 후 `https://<사용자명>.github.io/<저장소명>/` 에서 확인

> 루트에 `index.html`이 있으므로 별도 설정 없이 자동 서빙됩니다. `.nojekyll`이 있어 정적 파일이 그대로 게시됩니다.

## 데이터 집계 재현

`index.html`에 이미 데이터가 포함돼 있어 배포에는 재집계가 필요 없습니다. 원본에서 다시 만들려면:

```bash
pip install pandas
python3 scripts/aggregate.py    # → data/data_wellness.json 생성
# 생성된 JSON을 index.html의 `const DATA=...` 위치에 주입
```

집계 규칙 요약:
- 걸음·칼로리·활동·시간대별·심박: 2개 관측기간(2016-03-12~04-09, 04-12~05-12) **병합**
- 수면: 요약본(sleepDay)이 있는 **4/12~5/12, 24명만** 사용
- 사용자: 두 기간 합집합 **35명**
- 기록 지속성 = 기록일수 ÷ 전체 관측창(62일)

## 데이터 출처 및 유의사항

- 출처: Kaggle — **FitBit Fitness Tracker Data** (Möbius 업로드). 공개(CC0로 알려짐) 데이터이나, 배포 전 Kaggle 데이터셋 페이지의 License를 직접 확인하세요.
- 본 대시보드는 **2016년 공개 샘플(35명) 기반 프로토타입**입니다. 프로덕션에서는 동일 스키마를 자사 기기 텔레메트리에 연결합니다.
- 센서별 커버리지가 다릅니다: 심박 15명, 수면 24명. 각 지표에 표본 수를 병기했습니다.
- 수면 단계(깊은/얕은 잠) 원천 데이터가 없어 수면의 질은 **수면 효율**로 대체했습니다.
- 상관관계는 **인과관계가 아닙니다**. 해석 문구에도 명시돼 있습니다.

## 라이선스 / 비제휴

개인·사내 분석 목적의 프로토타입입니다. 특정 회사의 디자인 시스템·브랜드와 무관하며, 시각 스타일은 일반 디자인 토큰(Pretendard 폰트, 블루 계열 팔레트)만 사용합니다.
