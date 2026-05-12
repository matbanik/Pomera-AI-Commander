# NPM Token & GitHub Actions Publishing Guide

Runbook for rotating the npm granular access token used by CI/CD to publish `pomera-ai-commander` to npmjs.com.

---

## Overview

| Item | Value |
|------|-------|
| **Package** | [pomera-ai-commander](https://www.npmjs.com/package/pomera-ai-commander) |
| **npm Account** | `matbanik` |
| **GitHub Repo** | `matbanik/Pomera-AI-Commander` |
| **Secret Name** | `NPM_TOKEN` |
| **Token Type** | Granular Access Token |
| **Max Expiration** | 90 days |

---

## Step 1 — Generate a New npm Token

1. Go to: **https://www.npmjs.com/settings/matbanik/tokens/granular-access-tokens/new**
2. Fill in the form:

| Field | Value |
|-------|-------|
| **Token name** | `github-actions-publish` |
| **Description** | `CI/CD publish token for pomera-ai-commander` |
| **Bypass two-factor authentication (2FA)** | ☑ Checked |
| **Packages and scopes → Permissions** | **Read and write** |
| **Select packages** | `pomera-ai-commander` |
| **Organizations → Permissions** | No access |
| **Expiration** | **90 days** (maximum) |

3. Click **Generate token**
4. **Copy the token immediately** — it will not be shown again

> [!CAUTION]
> If you lose the token before saving it to GitHub, you must delete it and generate a new one.

---

## Step 2 — Update the GitHub Secret

1. Go to: **https://github.com/matbanik/Pomera-AI-Commander/settings/secrets/actions**
2. Find `NPM_TOKEN` in the repository secrets list
3. Click the **pencil icon** (Update)
4. Paste the new token value
5. Click **Save**

> [!NOTE]
> If `NPM_TOKEN` doesn't exist yet, click **New repository secret**, enter `NPM_TOKEN` as the name, paste the token, and save.

---

## Step 3 — Delete the Old Token (npm)

1. Go to: **https://www.npmjs.com/settings/matbanik/tokens**
2. Find the **old** `github-actions-publish` token (check the "Expires" date)
3. Click the token → scroll down → **Delete token**

---

## Step 4 — Verify

Run a publish to confirm the new token works:

```bash
# Trigger a release workflow, or test manually:
npm whoami --registry https://registry.npmjs.org/
```

Or push a version bump and verify the GitHub Actions publish workflow succeeds.

---

## Rotation Schedule

| Action | When |
|--------|------|
| **Generate new token** | Every ~85 days (before 90-day expiry) |
| **Set calendar reminder** | 7 days before expiration |
| **Verify after rotation** | Same day |

> [!TIP]
> Set a recurring calendar reminder for **7 days before expiration** to avoid CI/CD failures from an expired token.

---

## Troubleshooting

### `npm ERR! 401 Unauthorized`
- Token expired or was deleted → Rotate following this guide
- Wrong secret name → Verify `NPM_TOKEN` matches what the workflow expects

### `npm ERR! 403 Forbidden`
- Token doesn't have write permissions → Regenerate with **Read and write**
- Token scoped to wrong package → Verify `pomera-ai-commander` is selected

### Workflow file reference

The publish workflow lives at:
```
.github/workflows/publish.yml
```

It references the secret as:
```yaml
env:
  NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

---

## Token History

| Date | Expiry | Notes |
|------|--------|-------|
| 2026-04-15 | 2026-07-14 | Rotated; 90-day granular token |
| 2025-01-19 | 2026-04-16 | Original `github-actions-publish` token |
