# Nano Banana Image Generation — Status

## What it does

Generates hyper-realistic avatar images for personas using Google's Gemini API. The feature is branded "nano-banana" internally and is the default image generation model (with DALL-E as a fallback option).

## What's been done

- **`ImageGenerationService._generate_with_banana()`** — calls `client.models.generate_content()` with `response_modalities=["IMAGE", "TEXT"]` to generate images via Gemini flash models.
- **Config** — `GEMINI_API_KEY` and `GEMINI_MODEL_ID` added to `Settings` in `config.py`, with defaults and `.env.example` documentation.
- **`google-genai>=0.3.0`** added to `requirements.txt`.
- **Local avatar storage** — generated images are saved to `LOCAL_AVATAR_DIR` (defaults to `local_avatars/`) and served via FastAPI's `StaticFiles` mount at `/avatars/{filename}`.
- **Presigned URL handling** — `generate_presigned_url()` updated to handle local files, S3 keys, and full URLs.
- **Unit tests** — 26 tests pass covering prompt building, DALL-E path, nano-banana path (mocked), storage, and fallback behaviour.
- **All 382 backend tests pass** at 88%+ coverage.

## What's NOT working yet

### Gemini API billing required

The current API key is on the **free tier**, which has **zero quota** for all image generation models. Every image generation model available (Imagen 4.0, Gemini 2.5 Flash Image, Gemini 3.1 Flash Image Preview, etc.) returns `429 RESOURCE_EXHAUSTED` with `limit: 0`.

**To fix:** Enable billing on the Google AI project at https://ai.dev/projects.

### Model ID

The default model is `gemini-2.5-flash-image` (set in `config.py` and `.env`). This was verified to exist in the API model listing. The previous values (`imagen-3.0-generate-001`, `gemini-3.1-flash-image-preview`) were either removed or also require paid plans.

Available image models as of 2026-04-15:
- `gemini-2.5-flash-image` (recommended — cheapest)
- `gemini-3-pro-image-preview`
- `gemini-3.1-flash-image-preview`
- `imagen-4.0-generate-001` (uses different API: `generate_images` not `generate_content`)
- `imagen-4.0-ultra-generate-001`
- `imagen-4.0-fast-generate-001`

If switching to an Imagen model, `_generate_with_banana()` needs to be reverted to use `client.models.generate_images()` instead of `generate_content()`.

## Steps to complete

1. **Enable billing** on the Google Cloud / AI project linked to the Gemini API key.
2. **Test end-to-end** — create a persona via the UI or API and confirm an avatar image is generated and displayed.
3. **Verify the `.env` has the right key** — two keys exist: `AIzaSyAuGI7YBs653PerWWDNRkdwylCS6_1xnlU` and `AIzaSyBbAEH8HtOgUY5qJPIA6F00o59FT33G8z4`. Check which project has billing enabled.
4. **Optional:** pick a different model if `gemini-2.5-flash-image` quality isn't satisfactory.

## Key files

| File | Purpose |
|------|---------|
| `backend/app/services/image_generation_service.py` | Core service — prompt building, Gemini/DALL-E calls, storage |
| `backend/app/config.py` | `GEMINI_API_KEY`, `GEMINI_MODEL_ID`, `LOCAL_AVATAR_DIR` settings |
| `backend/.env` | Actual API key and model config |
| `backend/.env.example` | Template with commented Gemini config |
| `backend/requirements.txt` | `google-genai>=0.3.0` dependency |
| `backend/tests/unit/test_image_generation_service.py` | 26 unit tests |
| `backend/app/models/persona.py` | `to_dict()` calls `generate_presigned_url()` for avatar URLs |
