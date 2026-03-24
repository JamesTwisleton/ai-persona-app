# UI Overhaul Plan

## Summary of changes

| # | Item | Scope |
|---|---|---|
| 1 | Delete interface (personas + conversations) | Frontend |
| 2 | Superuser bulk delete | Backend + Frontend |
| 3 | Fix broken avatar images | Backend + Infra |
| 4 | Admin panel (user list + promote superuser) | Backend + Frontend |
| 5 | Select public personas in conversation creation | Backend + Frontend |
| 6 | Logo — JPEG → SVG, light/dark, branded everywhere | Frontend |
| 7 | Persona-centred discovery feed (2-col, photo-first) | Frontend |
| 8 | Conversation cards show participant avatars | Backend + Frontend |

---

## 1. Delete interface

### Current state
- Persona list page has a small hover-reveal ✕ button on PersonaCard
- No delete UI on the conversation list page at all
- No bulk selection anywhere

### Changes
**PersonaCard:** Replace the hidden hover button with a visible trash icon in the card footer. Add a confirmation modal (not `window.confirm`) with the persona's name and a red "Delete" CTA.

**Conversations list page:** Add a trash icon button to each conversation row. Same confirmation modal pattern.

**My Personas page / My Conversations page:** Add "Select" mode toggle button in the page header. When active:
- Checkboxes appear on each card/row
- "Select all" checkbox in the header
- "Delete selected (N)" red button appears
- Superusers see this mode on all public content in the admin panel too

---

## 2. Superuser bulk delete

### Admin panel route: `/admin`
- Only accessible to `is_superuser = true` users; redirect to `/` otherwise
- Three tabs: **Users**, **Personas**, **Conversations**

**Personas + Conversations tabs:**
- Table view with: avatar/name, owner, created date, view/upvote counts
- Checkbox per row + "Select all"
- "Delete selected" button calls `DELETE /personas/{id}/force` or `DELETE /conversations/{id}/force` for each
- Inline progress (N deleted, N failed)

**Backend:** No new endpoints needed — the force-delete endpoints from the social layer already exist. Need a new endpoint to list all personas/conversations (not just the current user's):
- `GET /admin/personas` — paginated, all users
- `GET /admin/conversations` — paginated, all users

These join with the users table to show owner info.

---

## 3. Fix broken avatar images

### Root cause
DALL-E image URLs (`oaidalleapiprodscus.blob.core.windows.net/...`) **expire after approximately 1 hour**. The database stores the temporary URL. Once it expires, the `<img>` tag returns 404.

### Fix: S3 avatar storage
1. **Terraform:** Add `aws_s3_bucket` (`persona-composer-avatars`) with public-read ACL and `aws_s3_bucket_policy`. Output the bucket name.
2. **IAM:** Add `s3:PutObject` / `s3:GetObject` permission to the ECS task role.
3. **ImageGenerationService:** Change to use `response_format="b64_json"`, decode the base64, upload to S3 as `avatars/{unique_id}.jpg`, return the permanent S3 URL (`https://persona-composer-avatars.s3.amazonaws.com/avatars/{unique_id}.jpg`).
4. **Existing broken records:** Add a one-time migration endpoint `POST /admin/repair-avatars` (superuser only) that iterates all personas with expired DALL-E URLs and regenerates them. Or add a note that existing broken avatars need re-generation.

### Local dev
Use environment detection — if `AWS_DEFAULT_REGION` is not set or `TESTING=1`, skip S3 and return the data URL or fallback avatar. Add `S3_AVATAR_BUCKET` env var.

---

## 4. Admin panel

### Route: `/admin`
Guard: redirect to `/` if `user.is_superuser !== true`.

**Users tab:**
- Table: avatar, name, email, joined date, persona count, `is_admin` badge, `is_superuser` badge
- "Promote to superuser" button per row (calls new endpoint)
- "Remove superuser" button if already superuser (can't demote self)

**Personas tab:** (described in §2)

**Conversations tab:** (described in §2)

### New backend endpoints
- `GET /admin/users` — list all users with counts (superuser only)
- `PATCH /admin/users/{id}/superuser` — set `is_superuser: true/false` (superuser only, can't self-demote)
- `GET /admin/personas` — all personas with owner info
- `GET /admin/conversations` — all conversations with owner info

---

## 5. Public personas in conversation creation

### Current state
Conversation creation only shows the current user's own personas.

### Change
Expand the persona picker to show two sections:
1. **My Personas** — user's own (existing behaviour)
2. **Public Personas** — other users' `is_public=true` personas, searchable by name

When a public persona is selected for a conversation, it is used as-is (not cloned). The conversation's persona participants include the foreign persona's `id`. The orchestrator already loads the persona from DB by ID, so no changes there.

**Backend:** Conversation creation currently validates `Persona.user_id == current_user.id`. Relax this to allow public personas:
```python
# Allow own personas OR public personas from others
.filter(or_(Persona.user_id == current_user.id, Persona.is_public == True))
```

**Frontend:**
- New `GET /personas/public` endpoint (or filter `GET /discover` personas)
- Two-section accordion in the persona picker
- Search input to filter the public personas list

---

## 6. Logo

### Source
`frontend/logo_raw.jpeg` — a human head profile silhouette (left-facing) with musical staff lines and notes flowing from the head in a blue-to-purple gradient. Stars/sparkles. Clean white background.

### Deliverable
`frontend/public/logo.svg` — hand-crafted SVG recreation:
- Uses `currentColor` where appropriate so it adapts to context
- Has two colour schemes via CSS custom properties or `prefers-color-scheme`:
  - **Light mode:** gradient from `#06b6d4` (cyan) to `#7c3aed` (violet), white background
  - **Dark mode:** same gradient, transparent/dark background
- Simplified faithful recreation of the head profile + flowing staff lines + notes
- Sized at 48×48 for favicon use, scales via `viewBox`

### Placement
- Navbar: logo left of "PersonaComposer" wordmark
- Login page: centred above the sign-in card
- Home page hero: larger version in the header
- Browser tab favicon: `frontend/public/favicon.svg`
- `<title>` tag: "PersonaComposer" everywhere (update `layout.tsx`)

---

## 7. Persona-centred discovery feed

### Changes to home page (`/`)
**Persona column:**
- 2 cards per row (CSS grid `grid-cols-2`)
- Each card is **photo-first**: avatar fills the top 60% of the card (aspect-ratio square), name + motto below
- Circular avatar with gradient border ring
- No text truncation on the photo itself

**My Personas page (`/personas`):**
- Same 2-col photo-first grid
- PersonaCard redesigned: avatar dominant (square top), name/motto/archetype below
- Existing delete functionality preserved

---

## 8. Conversation participant avatars

### Conversation cards (list + feed)

Each conversation card shows a **participant avatar strip** — up to 3 circular avatars overlapping (like AvatarGroup in many design systems), with "+N" if more.

**Backend change needed:** `Conversation.to_dict()` currently only includes messages when `include_messages=True`. The list endpoints don't include participant info. Need to add lightweight participant data (name + avatar_url) to the base `to_dict()` without the full message payload.

Add `include_participants: bool = False` to `to_dict()` and expose it in:
- `GET /conversations` — include participants
- `GET /discover` — include participants

**Frontend:** New `AvatarGroup` component, used in:
- Conversation cards on home discovery feed
- Conversation list page (`/conversations`)
- Conversation detail header

---

## Files changed summary

### Backend
| File | Change |
|---|---|
| `app/services/image_generation_service.py` | S3 upload, b64_json format |
| `app/routers/conversations.py` | Allow public personas; include participants in list |
| `app/routers/personas.py` | `GET /personas/public` endpoint |
| `app/routers/admin.py` | Add user list, promote superuser, all personas/conversations |
| `app/models/conversation.py` | `to_dict` participant summary |
| `app/config.py` | `S3_AVATAR_BUCKET` setting |
| `docker-entrypoint.sh` | No changes needed |

### Infrastructure
| File | Change |
|---|---|
| `terraform/s3_avatars.tf` (new) | S3 bucket + policy for avatars |
| `terraform/iam.tf` | Add S3 PutObject to ECS task role |
| `terraform/outputs.tf` | Output avatar bucket name |

### Frontend
| File | Change |
|---|---|
| `public/logo.svg` (new) | SVG logo |
| `public/favicon.svg` (new) | Favicon version |
| `app/layout.tsx` | Title, favicon, global metadata |
| `app/page.tsx` | 2-col persona grid, photo-first cards, participant avatars on convos |
| `app/personas/page.tsx` | 2-col photo-first grid, select mode + bulk delete |
| `app/conversations/page.tsx` | Delete button, participant avatars, select mode |
| `app/conversations/new/page.tsx` | Public persona picker with search |
| `app/admin/page.tsx` (new) | Admin panel — users, personas, conversations |
| `components/layout/Navbar.tsx` | Logo + "PersonaComposer" wordmark |
| `components/persona/PersonaCard.tsx` | Photo-first redesign |
| `components/social/AvatarGroup.tsx` (new) | Overlapping avatar strip |
| `components/ui/ConfirmModal.tsx` (new) | Reusable delete confirmation modal |

---

## Open questions for the user

### Q1 — Avatar storage in local dev
The S3 fix requires deploying Terraform changes for the S3 bucket. For local dev, avatars would fall back to the DiceBear placeholder. Is that acceptable, or do you want local dev to also persist images (e.g. into the Docker volume)?

### Q2 — Public personas in conversations
When a user adds someone else's public persona to their conversation, the conversation uses that persona's OCEAN profile and avatar, but the persona owner has no involvement. Two options:
- **(a) Use directly** — the foreign persona appears as a participant with their profile intact. The persona owner cannot see or remove it from the conversation.
- **(b) Shadow-clone** — a copy of the persona is made under the conversation creator's account when selected. The original owner is unaffected. Downside: diverges from the original over time.

Which do you prefer?

### Q3 — Logo faithfulness
The logo in `logo_raw.jpeg` appears to be a stock vector image (human profile + musical notes). Do you want me to faithfully recreate it as SVG (same motif: face + music notes), or use it as inspiration to create something more unique to PersonaComposer (e.g. face + speech bubbles, or face + OCEAN radar)?
