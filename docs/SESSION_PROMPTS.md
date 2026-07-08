# 세션 재현 기록 — wellness-dashboard

이 문서는 이번 세션에서 실행한 작업을 프롬프트 단위로 정리한 것이다. 동일한 순서로 따라 하면 같은 결과(문서화 → 배포 → 결과 요약)를 재현할 수 있다.

## 1. CLAUDE.md 생성

**프롬프트**
> `/init` — 이 코드베이스를 분석해서 향후 Claude Code가 참고할 CLAUDE.md를 만들어줘.

**수행 내용**
- [README.md](../README.md), [HANDOFF.md](../HANDOFF.md), [docs/PRD.md](PRD.md), [scripts/aggregate.py](../scripts/aggregate.py), [index.html](../index.html) 전체 구조 확인.
- 기존 CLAUDE.md·Cursor rules·Copilot instructions 없음을 확인.
- [CLAUDE.md](../CLAUDE.md) 신규 작성 — 아키텍처(단일 `index.html`, 인라인 `const DATA`, Chart.js 렌더링 패턴), 데이터 파이프라인(`aggregate.py` 병합/세그먼트 규칙), 로컬 실행법, GitHub Pages 배포 방식을 정리.

**재현 방법**: 동일 저장소에서 `/init` 실행.

## 2. GitHub Pages 배포

**프롬프트**
> github pages를 이용해서 배포해주고 연결이 필요하다면 connector를 이용해서 연결해

**진행 과정 및 결정**
1. 환경 점검 — `git status`(저장소 아님), `gh --version`(미설치), MCP 레지스트리에서 GitHub 커넥터 검색(결과 없음)을 확인.
2. 사용자에게 확인 질문 2개 후 답변 반영:
   - 연결 방식 → **gh CLI 설치 + 브라우저 로그인(디바이스 코드)**
   - 저장소명/공개범위 → **`wellness-dashboard` / public**
3. 실행한 명령 (순서대로):

```bash
brew install gh
gh auth login --hostname github.com --git-protocol https --web
# → 브라우저에서 https://github.com/login/device 접속, 터미널에 표시된 one-time code 입력해 인증
gh auth status   # 로그인 확인

git init
git add .
git commit -m "feat: wellness wearable insights dashboard"

gh repo create wellness-dashboard --public --source=. --remote=origin --push

gh api -X POST repos/<github-username>/wellness-dashboard/pages \
  -f "source[branch]=main" -f "source[path]=/"
```

4. 배포 검증:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://<github-username>.github.io/wellness-dashboard/   # 200 확인
curl -s https://<github-username>.github.io/wellness-dashboard/ | grep -o "<title>.*</title>"
curl -s https://<github-username>.github.io/wellness-dashboard/ | grep -c "const DATA="
curl -s -o /dev/null -w "%{http_code}\n" https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js
```

**결과**
- 저장소: https://github.com/gyeongwooworks-dev/wellness-dashboard
- 배포 URL: https://gyeongwooworks-dev.github.io/wellness-dashboard/

**재현 시 유의점**
- `gh auth login`은 브라우저 상호작용이 필요해 완전 자동화 불가 — 매번 사용자가 표시된 code를 직접 입력해야 함. 첫 시도에서 네트워크 오류(IPv6 라우팅 이슈)가 발생했으나 재시도로 해결됨.
- 이미 인증된 환경이면 1~2단계는 `gh auth status`로 확인 후 생략 가능.
- 대상 저장소가 이미 있으면 `gh repo create ...`는 실패하므로, 기존 remote에 `git push`만 수행.
- `.gitignore`가 `.DS_Store`·`*.csv`를 제외하므로 `git add .` 전 `git status`로 원치 않는 파일이 없는지 재확인.

## 3. 대시보드 결과 요약 (설문/문서용 텍스트)

**프롬프트**
> (설문 폼 스크린샷) "본인 대시보드 결과 정리 — 독자·KPI·차트·인사이트를 자유 형식으로 정리해주세요"에 답변해줘 → 이후 "지금까지 진행한 거를 프롬프트로 요약해서 재현성 있게 markdown으로 남겨줘"

**수행 내용**
- `index.html`에 인라인된 `const DATA=...` JSON을 파싱해 실제 KPI·세그먼트·페르소나·상관계수 수치를 추출.
- 독자 정의 → KPI 6개 나열 → 차트 9개(M1~M4, P1~P5) 요약 → 한 줄 인사이트 순서로 답변을 작성.

**재현 명령**
```bash
python3 -c "
import re, json
html = open('index.html', encoding='utf-8').read()
m = re.search(r'const DATA=(\{.*\});', html)
data = json.loads(m.group(1))
print('KPIS:', data['kpis'])
print('SEGMENTS:', data['segments'])
print('PERSONAS:', data['personas'])
print('SLEEP CORR:', data['sleepCorr'])
"
```

**추출된 값 (2026-07-08 기준 스냅샷)**
- KPI: 사용자 35명 · 평균 걸음 7,247보 · 평균 칼로리 2,264kcal · 평균 활성시간 33.1분 · 평균 수면효율 91.7% · 평균 기록지속성 63.3%
- 활동 세그먼트: 파워무버 7명 · 스테디 15명 · 라이트 13명
- 참여 세그먼트: 코어 1명 · 캐주얼 32명 · 이탈위험 2명
- 페르소나: 저녁형 파워무버(7명, 평균 12,437보) · 저녁형 스테디워커(15명, 평균 7,703보) · 오후형 라이트유저(13명, 평균 3,139보)
- 수면효율↔다음날 걸음 상관계수: r = -0.091

**최종 답변 전문**
> 이 페이지는 웰니스 웨어러블(FitBit 샘플, 35명·2016-03-12~05-12 62일 병합) 데이터를 마케팅팀(세분화·페르소나 활용)과 제품팀(행동 인사이트·리텐션 판단)이 공통 KPI 바 아래에서 각자 섹션을 보는 대시보드.
>
> KPI는 6개 — 첫번째는 사용자 수(35명), 두번째는 평균 걸음(7,247보), 세번째는 평균 칼로리(2,264kcal), 네번째는 평균 활성시간(33.1분), 다섯번째는 평균 수면효율(91.7%), 여섯번째는 평균 기록지속성(63.3%). 세그먼트 필터를 바꾸면 세그먼트 평균으로 즉시 갱신됨.
>
> 차트는 마케팅 4개 + 제품 5개, 총 9개:
> - M1 세그먼트 규모 — 활동량 도넛(파워무버 7명·스테디 15명·라이트 13명), 참여도 도넛(코어 1명·캐주얼 32명·이탈위험 2명)
> - M2 세그먼트 특성 레이더 — 걸음·칼로리·활성시간·수면효율·지속성 5개 지표 정규화 비교
> - M3 페르소나 카드 3장 — 저녁형 파워무버(7명, 평균 12,437보) / 저녁형 스테디워커(15명, 평균 7,703보) / 오후형 라이트유저(13명, 평균 3,139보), 카드마다 추천 메시지 방향 포함
> - M4 시간대별 활동 — 24시간 칼로리(막대)+활동강도(선) 콤보차트
> - P1 일별 추이 — 칼로리/걸음/활성시간 택1, 62일 라인·영역차트
> - P2 수면–활동 산점도 — 수면효율 vs 다음날 걸음 + 추세선
> - P3 지속성 — 지속성 구간별 분포 막대 + 주간 활성사용자 라인
> - P4 심박 — 최고활동일 분단위 심박 시계열 + 휴식/지방연소/유산소/고강도 존 비중 도넛
> - P5 커버리지 — 지표별 표본수 막대(활동 35명·심박 15명·수면 24명) + 정렬·검색 가능한 사용자 테이블
>
> 한 줄 인사이트: 참여 세그먼트는 캐주얼(지속성 40~80%)이 32명으로 전체의 91%를 차지해 코어 유저(1명) 전환 여지가 가장 크지만, 수면효율과 다음날 활동량의 상관은 r=-0.091로 사실상 없어 수면 개선만으로 활동 증가를 기대하긴 어렵다.

---

이 세 프롬프트를 이 저장소에 순서대로 적용하면(1 → 2 → 3) 동일한 CLAUDE.md 작성·GitHub Pages 배포·결과 요약을 재현할 수 있다. 데이터가 재집계(`scripts/aggregate.py` 재실행)되면 3번의 수치는 달라지므로 재추출이 필요하다.
