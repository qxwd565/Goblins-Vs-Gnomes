# Goblins Vs Gnomes: HSdeck API

한국 날짜(Asia/Seoul) 기준 고블린 대 노움 카드 API입니다. 143개 ID(수집 가능 123장, 생성 토큰·선택지·예비 부품 20개)를 유지합니다.

- `data/<ID>.json`: 최상위 키가 오름차순 날짜입니다. 최초 날짜에는 당시 확인 가능한 스펙, 이후 날짜에는 변경 필드만 기록합니다. 삭제는 `__remove`로 구분합니다.
- `metadata/<ID>.json`: 기존 원본 JSON 전체, 현재 카탈로그, 원시 자료, 출처 커밋, 신뢰도와 미확정 관측을 보존합니다.
- 기존 `cards.json`, `render.json`, `history.json`: 현재 플러그인을 위한 schema 1 호환 출력입니다. `cards.json` 바이트는 유지합니다.
- `cards-date.json`, `render-date.json`, `history-date.json`: 타입별 정확한 필드, 능력 목록, 삭제와 완전한 현재 상태를 제공하는 별도 출력입니다. 기존 플러그인의 주소를 이 파일로 바꾸면 안 됩니다.
- `release-policy.json`, `manifest.json`, `art/`, `golden/`: 기존 자료, ID와 경로를 유지합니다.

최초 한국 일반 덱 실사용일은 **2014-12-10**입니다. 클라이언트 사전 추가나 투기장 사전 체험과 구분합니다. 기존 55개 이벤트를 보존합니다. 야수/기계 복합 종족 4장(GVG_030/034/048/076)의 적용일은 출처에 따라 2022-11-30에서 **2023-02-15**로 바로잡습니다. 기존 이벤트 8개에는 검증된 키워드 능력 변경을 함께 기록합니다. 일반 효과 전체나 모든 엔진 플래그를 능력 목록으로 모델링한 것은 아닙니다.

**역사 검증은 부분 완료입니다.** 최초 한국어 표시 문구 99개의 차이, 함포 4.1 문구의 정확한 적용일, V-07-TR-0N 희귀도 변경 시점 등은 미확정입니다. 원본의 `rarity: null`은 해당 카드에서 미확정 값이지 역사적 희귀도 부재가 확인됐다는 뜻이 아닙니다. 모든 전체 최초 스펙은 `partially-verified` 상태입니다.

상세 형식과 호환 손실, 출처, 한계 및 전체 검사 명령은 [docs/date-schema.md](docs/date-schema.md)를 확인하세요. 이전 밸런스 감사는 [BALANCE-AUDIT.md](BALANCE-AUDIT.md), 재확인 출처는 `tools/gvg-date-recheck.json`에 있습니다.

빌드: `python3 tools/migrate-date-schema.py` 다음 `python3 tools/build-api.py`.

기본 검사: `python3 tools/test-gvg-history.py`, `python3 tools/test-date-schema.py`, `python3 tools/test-gvg-mechanics.py`, `python3 tools/test-legacy-compatibility.py`.

생성 번들을 직접 수정하지 말고 개별 날짜 원본을 고친 뒤 재생성합니다. 현재 원시 `nativeTags`를 과거 시점 스펙으로 해석하지 마세요. 원시 자료의 실제 개행은 보존하며 표시 문구만 `<br></br>` 형식을 씁니다. 플러그인 변경이나 실사이트 가져오기는 이 저장소 작업에 포함하지 않습니다.
