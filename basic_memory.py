"""Memoria de JARVIS: lectura y guardado directos en Supabase."""

from uuid import UUID
from datetime import datetime, timedelta, timezone

from supabase import create_client


class BasicMemory:
    def __init__(self, session_id, max_messages=20, supabase_url="", supabase_key=""):
        if not supabase_url or not supabase_key:
            raise ValueError("Configura SUPABASE_URL y SUPABASE_KEY.")
        self.session_id = str(UUID(str(session_id)))
        self.max_messages = max_messages
        self.client = create_client(supabase_url, supabase_key)
        self._cache = self._cargar_historial()

    def _cargar_historial(self):
        response = (self.client.table("jarvis_messages")
                    .select("role, content").eq("session_id", self.session_id)
                    .order("created_at", desc=True).limit(self.max_messages).execute())
        return list(reversed(response.data or []))

    def messages(self):
        return [dict(message) for message in self._cache[-self.max_messages:]]

    def add_turn(self, user_text, assistant_text):
        now = datetime.now(timezone.utc)
        rows = [{"session_id": self.session_id, "role": role, "content": content,
                 "created_at": (now + timedelta(microseconds=i)).isoformat()}
                for i, (role, content) in enumerate([("user", user_text), ("assistant", assistant_text)])]
        # Guarda pregunta y respuesta juntas; actualiza la memoria solo al confirmar.
        self.client.table("jarvis_messages").insert(rows).execute()
        self._cache.extend({"role": row["role"], "content": row["content"]} for row in rows)
        self._cache = self._cache[-self.max_messages:]
