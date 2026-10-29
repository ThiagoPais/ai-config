# Verification report example

A verification report has three parts: a per-criterion breakdown, the actual test/build/lint results, and a summary table. Match the issue's own language and status wording (e.g. keep ✅/⚠️/❌ but translate the surrounding words). Cite real files and real numbers — a report that says "tests pass" without a count is a report nobody can spot-check.

The closing line is a promise. Only write it after the human has said which gaps become tracked issues — don't pre-commit to opening tickets for things that turn out to be expected behavior or out of scope.

## Worked example (Portuguese, real repo)

This was posted as a comment on the issue, after the user reviewed the draft and asked to remove two items that turned out not to be problems (a route intentionally requiring logout-before-relogin, and a dashboard route with no component yet because that screen simply hadn't been built):

```markdown
## ✅ Verificação de Implementação

Validado localmente na branch `login-front` (commit ca8632a) em 2026-09-22, cruzando os critérios de aceite com o código e reexecutando os testes/build.

### Critérios de Aceite

1. **Cadastro e Login (Local e Google)** — ✅ Atendido
   - Tela de Cadastro (`SignupFront`) com e-mail e senha, enviando `POST /api/auth/register`.
   - Login atualizado com e-mail/senha e botão de Google SSO via Google Identity Services, obtendo `clientId` dinamicamente do backend.
2. **Gerenciamento de Estado e Expiração** — ⚠️ Parcialmente atendido
   - `AuthService` armazena token/usuário via Angular Signals, sincronizado com `localStorage`. ✅
   - **Pendente:** o `HttpInterceptor` (`auth.interceptor.ts`) apenas injeta o header `Authorization`, mas não captura erros `401`, não limpa o storage/estado e não redireciona para `/login` quando o token expira.
3. **Vinculação Transparente de Contas (Auto-link)** — ✅ Atendido do lado do frontend (fluxo depende do backend).
4. **Recuperação de Senha** — ✅ Atendido
   - `ForgotPasswordFront` (`/forgot-password`) e `ResetPasswordFront` (`/reset-password?token=...`) implementados.
5. **Proteção de Rotas** — ✅ Atendido
   - `authGuard` implementado e aplicado à rota `/dashboard`. O conteúdo do dashboard ainda não foi implementado, o que é esperado nesta etapa do projeto.

### Testes e Build
- `npm test -- --watch=false`: ✅ Passou (6 suites, 7 testes).
- `npm run build`: ⚠️ Passou com alerta — `login-front.css` excedeu o orçamento de 4.00 kB, atingindo 6.98 kB (será tratado internamente, sem necessidade de issue).
- **Cobertura de testes:** apenas `login-front.spec.ts` existe entre os novos componentes, testando só a instanciação (`should create`). Não há testes para `AuthService`, `authGuard`, `authInterceptor`, `SignupFront`, `ForgotPasswordFront` ou `ResetPasswordFront`.

### Resumo
| Item | Status |
| :--- | :--- |
| Captura de erro 401 no interceptor | ❌ Faltando |
| Testes unitários dos novos recursos | ❌ Faltando |
| Orçamento de CSS do login | ⚠️ Estourado (tratado internamente) |

Vou abrir issues específicas para as pendências de interceptor e testes para acompanhamento individual.
```

Notice what changed between the draft and the posted version: two rows that were originally flagged as problems (a routing "bug" that was actually intended product behavior, and a dashboard route missing a component that simply hadn't been built yet) were removed entirely rather than downgraded — because they weren't gaps at all once the human clarified intent. Two other items (a CSS budget warning and a lint failure) stayed in the report as facts but were explicitly marked "tratado internamente" and dropped from the closing promise, because the team chose to fix them without a tracked issue. This is the normal shape of a second draft: the first pass is your best technical read of the diff; the human's context about what's intentional, in-progress, or out-of-scope always wins.
