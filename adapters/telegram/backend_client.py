"""
Thin HTTP client для вызовов backend API из Telegram adapter.
Все методы соответствуют backend endpoints из WAVE 4-8.
"""

import aiohttp

from adapters.telegram.config import BACKEND_URL


class BackendClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base = BACKEND_URL

    async def _post(
        self,
        path: str,
        json: dict | None = None,
        token: str | None = None,
        data: aiohttp.FormData | None = None,
    ) -> dict:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        async with self.session.post(
            f"{self.base}{path}",
            json=json if data is None else None,
            data=data,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _patch(self, path: str, json: dict, token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        async with self.session.patch(
            f"{self.base}{path}",
            json=json,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _get(self, path: str, token: str | None = None) -> dict:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        async with self.session.get(
            f"{self.base}{path}",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    # Auth
    async def phone_start(self, phone: str) -> dict:
        return await self._post("/auth/phone/start", {"phone": phone})

    async def phone_verify(self, phone: str, code: str) -> dict:
        return await self._post("/auth/phone/verify", {"phone": phone, "code": code})

    # Intake
    async def create_intake_case(self, token: str, branch: str) -> dict:
        return await self._post("/intake/cases", {"branch": branch}, token=token)

    async def get_intake_case(self, token: str, case_id: str) -> dict:
        return await self._get(f"/intake/cases/{case_id}", token=token)

    async def set_resident_count(self, token: str, case_id: str, count: int) -> dict:
        return await self._patch(
            f"/intake/cases/{case_id}/residents/count",
            {"resident_count": count},
            token=token,
        )

    async def confirm_ocr(
        self,
        token: str,
        case_id: str,
        order_index: int,
        ocr_data: dict,
        confirmed: bool,
    ) -> dict:
        return await self._patch(
            f"/intake/cases/{case_id}/residents/{order_index}/ocr",
            {"ocr_data": ocr_data, "confirmed": confirmed},
            token=token,
        )

    async def submit_intake(self, token: str, case_id: str) -> dict:
        return await self._post(f"/intake/cases/{case_id}/submit", token=token)

    async def upload_passport(
        self,
        token: str,
        case_id: str,
        order_index: int,
        image_bytes: bytes,
        filename: str = "passport.jpg",
    ) -> dict:
        form = aiohttp.FormData()
        form.add_field(
            "file", image_bytes, filename=filename, content_type="image/jpeg"
        )
        return await self._post(
            f"/intake/cases/{case_id}/residents/{order_index}/passport",
            token=token,
            data=form,
        )

    async def upload_extra_doc(
        self,
        token: str,
        case_id: str,
        file_bytes: bytes,
        file_type: str,
        filename: str,
        content_type: str = "image/jpeg",
    ) -> dict:
        form = aiohttp.FormData()
        form.add_field(
            "file", file_bytes, filename=filename, content_type=content_type
        )
        path = f"/intake/cases/{case_id}/extra-docs?file_type={file_type}"
        return await self._post(path, token=token, data=form)
