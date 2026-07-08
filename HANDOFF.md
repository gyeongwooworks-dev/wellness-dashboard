# Claude Code 인수인계 노트 — GitHub Pages 배포

이 폴더(`wellness-dashboard/`)를 GitHub Pages로 배포하는 작업입니다. 대시보드 자체는 완성돼 있고, **배포만** 하면 됩니다.

## 배포 목표
`wellness-dashboard/` 를 새 GitHub 저장소로 올리고, GitHub Pages로 공개 URL을 만든다.

## 전제 / 확인 필요
- GitHub 계정 및 `gh` CLI 로그인 상태(또는 원격 저장소 URL). 없으면 사용자에게 요청.
- 저장소 공개 범위(public/private). Pages는 무료 플랜에서 public 저장소가 필요할 수 있음 → 사용자에게 확인.
- 커밋 계정 정보(user.name/email).

## 배포 절차 (예시 명령)
```bash
cd wellness-dashboard
git init
git add .
git commit -m "feat: wellness wearable insights dashboard"

# 원격 저장소 생성 + 연결 (gh CLI 사용 시)
gh repo create wellness-dashboard --public --source=. --remote=origin --push
# 또는 수동:
# git remote add origin https://github.com/<user>/<repo>.git
# git branch -M main && git push -u origin main
```

배포 활성화:
- `gh` 사용 시: `gh api -X POST repos/<user>/<repo>/pages -f "source[branch]=main" -f "source[path]=/"` (또는 Settings→Pages에서 수동)
- 수동: 저장소 **Settings → Pages → Source: main / (root)** 저장

## 배포 후 검증
- `https://<user>.github.io/<repo>/` 접속 → 대시보드 렌더 확인
- 콘솔 에러 없는지, Chart.js/Pretendard CDN 로드되는지 확인
- KPI·세그먼트 필터, 사용자 드릴다운 동작 확인

## 주의
- `index.html`은 자체 완결형이며 데이터가 인라인 포함됨 → 빌드 스텝 없음.
- `.nojekyll` 유지(정적 파일 그대로 게시).
- 원본 FitBit CSV·기타 무관한 폴더는 이 저장소에 포함하지 말 것(현재 폴더에 없음).
- 배포는 되돌릴 수 있으나, 저장소를 **public**으로 만드는 것과 최초 **push**는 사용자 확인 후 진행.
