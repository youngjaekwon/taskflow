# CLAUDE.md — @taskflow/web

SvelteKit 기반 프론트엔드 앱. 백엔드의 GraphQL API를 소비하여 태스크 관리 UI를 제공한다.

## 기술 스택

| 영역 | 기술 |
|------|------|
| 프레임워크 | SvelteKit 2 + Svelte 5 |
| 언어 | TypeScript (strict) |
| 런타임 | Node 22 |
| 빌드 | Vite |
| 스타일링 | Tailwind CSS v4 + Svelte 스코프드 스타일 |
| 테스트 | Vitest (단위/컴포넌트) + Playwright (E2E) |
| GraphQL | SvelteKit fetch 직접 사용 (별도 클라이언트 라이브러리 없음) |

## 포트 및 환경

- **개발 서버**: `http://localhost:5173`
- **GraphQL 엔드포인트**: 환경 변수 `GRAPHQL_ENDPOINT`로 설정
  - backend-graphene: `http://localhost:8001/graphql`
  - backend-strawberry: `http://localhost:8002/graphql`

## 주요 명령어

```bash
# 모노레포 루트에서 실행
pnpm dev --filter @taskflow/web    # 개발 서버
pnpm build --filter @taskflow/web  # 프로덕션 빌드
pnpm test --filter @taskflow/web   # 테스트 실행
pnpm lint --filter @taskflow/web   # 린트 + 포매팅 검사

# apps/web 디렉터리에서 실행
pnpm dev
pnpm build
pnpm test:unit           # Vitest 단위/컴포넌트 테스트
pnpm test:e2e            # Playwright E2E 테스트
pnpm lint
pnpm check               # svelte-check 타입 검사
```

## 프로젝트 구조

```
apps/web/
├── src/
│   ├── routes/              # 파일시스템 기반 라우팅
│   │   ├── +page.svelte     # 홈 페이지
│   │   ├── +layout.svelte   # 루트 레이아웃
│   │   └── boards/
│   │       ├── +page.svelte
│   │       └── [id]/
│   │           └── +page.svelte
│   ├── lib/                 # 재사용 코드 ($lib 별칭)
│   │   ├── components/      # 공유 UI 컴포넌트
│   │   ├── server/          # 서버 전용 코드 (클라이언트 임포트 불가)
│   │   │   └── graphql.ts   # GraphQL 요청 유틸리티
│   │   ├── graphql/         # GraphQL 쿼리/뮤테이션 정의
│   │   │   ├── queries/
│   │   │   ├── mutations/
│   │   │   └── fragments/
│   │   ├── stores/          # 공유 상태 (.svelte.ts)
│   │   ├── types/           # TypeScript 타입 정의
│   │   └── utils/           # 유틸리티 함수
│   ├── params/              # 라우트 파라미터 매처
│   ├── app.html             # HTML 템플릿
│   ├── app.css              # 글로벌 CSS (Tailwind 임포트)
│   ├── app.d.ts             # 앱 전역 타입 (App namespace)
│   ├── error.html           # 치명적 에러 폴백
│   ├── hooks.server.ts      # 서버 훅
│   └── hooks.client.ts      # 클라이언트 훅
├── static/                  # 정적 에셋
├── tests/                   # Playwright E2E 테스트
├── svelte.config.js
├── vite.config.ts
└── tsconfig.json
```

## 개발 컨벤션

### Svelte 5 Runes 전면 사용

Svelte 5 runes 문법을 사용한다. 레거시 `let` 반응형, `$:`, `on:` 디렉티브, `<slot>` 등은 사용하지 않는다.

```svelte
<script lang="ts">
  // Props: $props() 사용
  let { title, children }: Props = $props();

  // 반응형 상태: $state 사용
  let count = $state(0);

  // 파생 상태: $derived 사용
  let doubled = $derived(count * 2);

  // 사이드 이펙트: $effect 사용
  $effect(() => { console.log(count); });
</script>

<!-- 콘텐츠 슬롯 대신 Snippet + {@render} 사용 -->
{@render children()}
```

**Rune 요약**:

| Rune | 용도 |
|------|------|
| `$state` | 반응형 상태 선언 |
| `$state.raw` | 프록시 없는 상태 (큰 읽기 전용 데이터에 사용) |
| `$derived` / `$derived.by` | 파생 값 (사이드 이펙트 금지) |
| `$effect` / `$effect.pre` | 사이드 이펙트 (DOM 업데이트 후/전) |
| `$props` | 컴포넌트 props 선언 |
| `$bindable` | 양방향 바인딩 가능 prop |
| `$inspect` | 디버깅 전용 (프로덕션에서 제거됨) |

### 이벤트 핸들링

`on:` 디렉티브 대신 props로 콜백을 전달한다:

```svelte
<!-- 컴포넌트 정의 -->
<script lang="ts">
  let { onclick }: { onclick?: (e: MouseEvent) => void } = $props();
</script>
<button {onclick}>클릭</button>

<!-- 사용 측 -->
<Button onclick={() => handleClick()} />
```

### 컴포넌트 패턴 — Snippets

`<slot>` 대신 Snippet을 사용한다:

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    children: Snippet;
    footer?: Snippet;
  }

  let { children, footer }: Props = $props();
</script>

<div>{@render children()}</div>
{#if footer}{@render footer()}{/if}
```

### 타입 시스템

- 모든 `.svelte` 파일에 `<script lang="ts">` 사용
- SvelteKit 자동 생성 타입(`$types`)을 활용하여 load, actions 타입 안전성 확보
- `src/app.d.ts`에서 `App.Locals`, `App.Error`, `App.PageData` 정의

```typescript
// +page.server.ts — 타입은 $types에서 자동 임포트
import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
  return { boardId: params.id };
};
```

```svelte
<!-- +page.svelte -->
<script lang="ts">
  import type { PageProps } from './$types';
  let { data }: PageProps = $props();
</script>
```

## 라우팅

### 라우트 파일 역할

| 파일 | 역할 | 실행 위치 |
|------|------|-----------|
| `+page.svelte` | 페이지 UI | 서버(SSR) + 브라우저 |
| `+page.server.ts` | 서버 전용 load + form actions | 서버만 |
| `+page.ts` | 유니버설 load | 서버 + 브라우저 |
| `+layout.svelte` | 레이아웃 (하위 경로에 적용) | 서버(SSR) + 브라우저 |
| `+layout.server.ts` | 서버 전용 레이아웃 load | 서버만 |
| `+server.ts` | API 엔드포인트 | 서버만 |
| `+error.svelte` | 에러 바운더리 | 서버(SSR) + 브라우저 |

### 동적 라우트

- `[id]` — 필수 파라미터
- `[[optional]]` — 선택적 파라미터
- `[...rest]` — 나머지 파라미터
- `(group)` — 라우트 그룹 (URL에 영향 없음)
- `[id=integer]` — 파라미터 매처 (`src/params/integer.ts`)

## 데이터 로딩

### 서버 load 우선 사용

GraphQL 요청은 `+page.server.ts`의 서버 load에서 수행한다. 시크릿 보호와 SSR 최적화를 위해 서버 전용 load를 기본으로 한다.

```typescript
// src/routes/boards/+page.server.ts
import { graphqlRequest } from '$lib/server/graphql';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
  const data = await graphqlRequest(fetch, BOARDS_QUERY, { first: 20 });
  return { boards: data.boards };
};
```

### 스트리밍 (비차단 데이터)

중요하지 않은 데이터는 await 없이 반환하여 스트리밍한다:

```typescript
export const load: PageServerLoad = async ({ fetch }) => {
  return {
    board: await fetchBoard(fetch),     // 차단: 렌더링 전 대기
    comments: fetchComments(fetch)       // 스트리밍: Promise 그대로 반환
  };
};
```

### 무효화

```typescript
// load에서 의존성 등록
export const load: PageLoad = async ({ fetch, depends }) => {
  depends('app:boards');
  // ...
};

// 컴포넌트에서 무효화 트리거
import { invalidate } from '$app/navigation';
invalidate('app:boards');
```

## GraphQL 통합

별도 GraphQL 클라이언트 라이브러리 없이 SvelteKit의 `fetch`를 직접 사용한다. SSR 호환성 문제가 없고 의존성이 최소화된다.

```typescript
// src/lib/server/graphql.ts
import { GRAPHQL_ENDPOINT } from '$env/static/private';

export async function graphqlRequest<T>(
  fetch: typeof globalThis.fetch,
  query: string,
  variables?: Record<string, unknown>
): Promise<T> {
  const response = await fetch(GRAPHQL_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables })
  });
  const { data, errors } = await response.json();
  if (errors) throw new Error(errors[0].message);
  return data as T;
}
```

### 쿼리/뮤테이션 조직

```
src/lib/graphql/
├── queries/       # query 문자열 모음
│   ├── boards.ts
│   └── tasks.ts
├── mutations/     # mutation 문자열 모음
│   ├── boards.ts
│   └── tasks.ts
└── fragments/     # 공유 fragment
    └── task.ts
```

## Form Actions

### 서버 액션 + 프로그레시브 인핸스먼트

```typescript
// +page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
  create: async ({ request, fetch }) => {
    const formData = await request.formData();
    const title = formData.get('title');
    if (!title) return fail(400, { title, missing: true });
    // ... GraphQL mutation
    redirect(303, `/tasks/${id}`);
  }
};
```

```svelte
<!-- +page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { PageProps } from './$types';
  let { form }: PageProps = $props();
</script>

<form method="POST" action="?/create" use:enhance>
  <input name="title" value={form?.title ?? ''} />
  {#if form?.missing}<p class="error">제목을 입력하세요</p>{/if}
  <button type="submit">생성</button>
</form>
```

## 상태 관리

### 컴포넌트 내 상태 — `$state` / `$derived`

### 모듈 간 공유 상태 — `.svelte.ts` 파일

```typescript
// src/lib/stores/counter.svelte.ts
function createCounter(initial = 0) {
  let count = $state(initial);
  return {
    get count() { return count; },
    increment() { count += 1; }
  };
}
export const counter = createCounter();
```

> `$state` 값을 직접 export하면 반응성이 깨진다. 반드시 getter/setter 패턴을 사용할 것.

### 컴포넌트 트리 상태 전달 — Context API

```svelte
<!-- 부모 --> setContext('key', value);
<!-- 자식 --> const value = getContext<Type>('key');
```

### 페이지 상태 접근 — `$app/state`

```typescript
import { page } from '$app/state';
page.url; page.params; page.data; page.form; page.error;
```

## 환경 변수

| 모듈 | 접근 범위 | 시점 | 용도 |
|------|-----------|------|------|
| `$env/static/private` | 서버만 | 빌드타임 | `GRAPHQL_ENDPOINT`, API 시크릿 |
| `$env/static/public` | 서버+클라이언트 | 빌드타임 | `PUBLIC_APP_NAME` |
| `$env/dynamic/private` | 서버만 | 런타임 | 런타임 시크릿 |
| `$env/dynamic/public` | 서버+클라이언트 | 런타임 | 런타임 공개 설정 |

- `PUBLIC_` 접두사가 있어야 클라이언트에서 접근 가능
- 시크릿은 절대 `PUBLIC_` 접두사를 사용하지 않는다
- `$lib/server/` 하위 코드는 클라이언트에서 임포트 시 빌드 에러 발생

## 에러 처리

### 예상 에러

```typescript
import { error } from '@sveltejs/kit';
error(404, 'Not found');
error(403, { message: 'Forbidden', code: 'AUTH_REQUIRED' });
```

### 에러 바운더리

`+error.svelte`는 가장 가까운 상위 경로에서 찾아 올라간다. 루트 `+error.svelte`가 최종 폴백.

### 에러 훅

- `hooks.server.ts`의 `handleError` — 서버 에러 로깅/트래킹
- `hooks.client.ts`의 `handleError` — 클라이언트 에러 로깅
- `error.html` — `+error.svelte`마저 렌더링 실패 시 최후의 폴백

## 스타일링

### Tailwind CSS v4

```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()]  // tailwindcss()가 sveltekit() 앞에 위치
});
```

```css
/* src/app.css */
@import "tailwindcss";
```

`<style>` 블록에서 `@apply` 사용 시 `@reference`가 필요:

```svelte
<style>
  @reference "../app.css";
  .btn { @apply px-4 py-2 bg-blue-500 text-white rounded; }
</style>
```

### Svelte 스코프드 스타일

- `<style>` 내 스타일은 해당 컴포넌트에만 적용
- `:global()` 선택자로 스코핑 해제
- CSS 변수를 통한 컴포넌트 커스터마이징: `<Card --card-bg="blue" />`

### 동적 클래스 (Svelte 5.16+)

```svelte
<div class={{ active: isActive, disabled: !clickable }}>...</div>
<div class={['base', isActive && 'active']}>...</div>
```

## 테스팅

### 단위/컴포넌트 테스트 (Vitest)

- 소스 파일 옆에 `.test.ts` 또는 `.svelte.test.ts` 배치
- Runes를 사용하는 테스트는 파일명에 `.svelte.test.ts` 필수
- 컴포넌트 테스트는 DOM 구조가 아닌 사용자 상호작용 중심으로 작성

```typescript
// src/lib/utils/format.test.ts
import { describe, it, expect } from 'vitest';

describe('format', () => {
  it('formats date', () => { /* ... */ });
});
```

### E2E 테스트 (Playwright)

- `tests/` 디렉터리에 배치
- 실제 브라우저 환경에서 전체 플로우 검증

```typescript
// tests/boards.test.ts
import { expect, test } from '@playwright/test';

test('보드 목록 표시', async ({ page }) => {
  await page.goto('/boards');
  await expect(page.getByRole('heading', { name: '보드' })).toBeVisible();
});
```

## 성능

### 프리로딩

```svelte
<!-- 마우스 호버 시 데이터 프리로드 -->
<a href="/boards" data-sveltekit-preload-data="hover">보드</a>
```

### SSR/CSR/Prerender 제어

```typescript
// +page.ts 또는 +layout.ts
export const ssr = true;         // 기본값
export const csr = true;         // 기본값
export const prerender = false;  // true면 빌드 시 정적 생성
```

### 큰 데이터 최적화

자주 변경되지 않는 큰 데이터셋에는 `$state.raw`를 사용하여 프록시 오버헤드를 방지한다.

## 보안

- SvelteKit이 form actions에 CSRF 토큰을 자동 관리
- `{@html}` 사용 시 반드시 새니타이즈 (XSS 방지). 가능하면 `{textContent}` 사용 (자동 이스케이프)
- 시크릿은 `$env/static/private` 또는 `$env/dynamic/private`에만 저장
- `$lib/server/` 디렉터리로 서버 전용 코드를 물리적으로 격리
- `hooks.server.ts`에서 `X-Frame-Options`, `X-Content-Type-Options` 등 보안 헤더 설정
