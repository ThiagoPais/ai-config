# Issue template examples

Use these only as a fallback when the target repo has no prior issues to learn style from. When the repo already has issues, mimic *those* instead — language, heading names, emoji, title prefix, everything. Consistency with the existing backlog matters more than any of these specific templates.

## Generic default template (English)

Title: `[Feature] <short, specific title>` (or `[Bug] <short, specific title>` for a defect)

```markdown
# [Feature] <title>

## User Story
As a <actor>, I want <action>, so that <benefit>.

## Acceptance Criteria

1. **<Criterion name>:**
   - <detail>
   - <detail>
2. **<Criterion name>:**
   - <detail>
```

Keep each numbered criterion checkable on its own — something a reviewer could look at the diff and answer yes/no to. Sub-bullets hold the supporting detail, not new requirements.

## Worked example (Portuguese, real repo style)

This is what a good breakdown looks like when the source requirement is a full feature ("implement authentication") rather than a single small ask — it splits into five criteria, each independently checkable, with the awkward edge cases (auto-link, TTL, token-in-URL) called out explicitly rather than left implicit:

```markdown
# [Feature] Implementar Fluxo de Autenticação, Cadastro e Recuperação de Conta

## 📖 História de Usuário
Como usuário, quero poder me cadastrar, fazer login (via E-mail ou Google) e recuperar minha senha caso a esqueça, para gerenciar minha conta de forma segura.

## 🎯 Critérios de Aceite

1. **Cadastro e Login (Local e Google):**
   - Criar tela de Cadastro (Sign Up) com E-mail e Senha.
   - Atualizar tela de Login para suportar E-mail/Senha e o botão de Google SSO.
   - Enviar senhas em texto plano via POST (HTTPS garantirá a segurança).
2. **Gerenciamento de Estado e Expiração:**
   - Armazenar o JWT e dados do usuário via Angular Signals (`AuthService`).
   - O JWT tem validade de 2 horas. O `HttpInterceptor` deve capturar erros `401 Unauthorized`, limpar o estado/storage e redirecionar para a tela de Login.
3. **Vinculação Transparente de Contas (Auto-link):**
   - O fluxo não deve exigir login prévio caso o e-mail retornado pelo Google SSO já exista. O backend fará o vínculo automático e retornará o token.
4. **Recuperação de Senha (Esqueci minha senha):**
   - Criar tela solicitando o e-mail do usuário.
   - Criar tela de "Redefinir Senha" que recebe o token via URL (ex: `/reset-password?token=abc`) e solicita a nova senha.
5. **Proteção de Rotas:**
   - Implementar `AuthGuard` para bloquear acesso ao Dashboard sem um token válido.
```

## Worked example of a follow-up issue (scoped gap from a verification pass)

Follow-up issues found during verification use the exact same template as any other issue — they're not a special second format. Title and body stay tight and reference where the gap was found:

```markdown
# [Feature] Tratar expiração de sessão (401) no HttpInterceptor

## 📖 História de Usuário
Como usuário, quero ser redirecionado automaticamente para a tela de login quando meu token expirar ou for invalidado, para não ficar preso em uma tela que não funciona mais.

## 🎯 Critérios de Aceite

1. **Captura de Erro 401:**
   - O `authInterceptor` deve capturar respostas HTTP `401 Unauthorized` de qualquer requisição à API.
2. **Limpeza de Sessão:**
   - Ao capturar um `401`, o interceptor deve limpar o token e os dados do usuário do `AuthService` (signals e `localStorage`).
3. **Redirecionamento:**
   - Após limpar a sessão, o usuário deve ser redirecionado para `/login`.

Referência: pendência identificada na verificação da issue #1 (comentário de 2026-09-22).
```
