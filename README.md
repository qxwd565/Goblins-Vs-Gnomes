# Goblins Vs Gnomes — HSdeck API

한국 날짜(Asia/Seoul)의 고블린 대 노움 카드 API입니다. 143개 ID(수집 가능 123장, 생성 토큰·선택지·예비 부품 20개)를 포함합니다.

- `data/<ID>.json`: schemaVersion 2. `card`에 최초 스펙, `card.patches`에 날짜별 변경 필드만 기록합니다.
- `cards.json`: 현재 카드 데이터.
- `render.json`: 현재 데이터와 과거 날짜 구간별 변경값.
- `history.json`: 이전 HScard 플러그인을 위한 호환 인덱스.
- `release-policy.json`: 실제 한국 정식 덱 사용 가능일. 투기장 사전 체험과 구분합니다.
- `manifest.json`: 데이터 수량 및 검증 범위.
- `art/`, `golden/`: 기존 파일과 경로를 유지합니다.

최초 한국 정식 사용일은 **2014-12-10**입니다. 29개 클라이언트 빌드에서 전 143종의 최초 수치·타입 등을 교차검증했고, 45종에 55개 날짜 이벤트를 기록했습니다. 현재값의 의미는 바꾸지 않았으며 카드 표시 줄바꿈은 `<br></br>`로 통일했습니다.

**검증은 부분 완료입니다.** 99종의 최초 표시 문구는 아직 현재 정규화 문구와 다릅니다. 모든 `initialSpecStatus`는 `partially_verified`이며, 최초 원문·이후 관측 구간·카드별 미확정 사항은 [BALANCE-AUDIT.md](BALANCE-AUDIT.md)와 `tools/gvg-release-audit.json`을 확인하세요. 날짜가 불명확한 문구 변경을 임의 날짜로 만들지 않습니다.

`historicalTextObservations`, `nativeRawText`, `nativeTags`는 원시 증거를 보존하며 표시용 줄바꿈 정규화 대상이 아닙니다. `nativeTags`를 과거 시점 스펙으로 해석하지 마세요.

## 빌드와 검사

`python3 tools/build-api.py`

`python3 tools/test-gvg-history.py`

생성 인덱스를 직접 수정하지 말고 개별 `data` 원본을 수정한 뒤 빌드합니다. 카드 이름이 아닌 정확한 ID/dbfId로 이력을 연결합니다. 현재 번들, 날짜 경계, 원시 증거, 두 번 재실행 동일성을 검사합니다.
