"""Memoria de una conversación. Nunca se comparte un cliente/cache entre visitantes."""

from uuid import UUID
from datetime import datetime, timedelta, timezone

from supabase import create_client


class BasicMemory:
    def __init__(self, session_id, max_messages=20, supabase_url="", supabase_key=""):
        self.session_id = str(UUID(str(session_id)))
        self.max_messages = max_messages
        self._cache = []
        self.client = None
        self.persistence_error = False
        if supabase_url and supabase_key:
            try:
                self.client = create_client(supabase_url, supabase_key)
                response = (self.client.table("jarvis_messages")
                            .select("role, content").eq("session_id", self.session_id)
                            .order("created_at", desc=True).limit(max_messages).execute())
                self._cache = list(reversed(response.data or []))
            except Exception:
                # Ningún error imprime claves, URL privada ni contenido de otras sesiones.
                self.persistence_error = True
                self.client = None

    def messages(self):
        return [dict(message) for message in self._cache[-self.max_messages:]]

    def add_turn(self, user_text, assistant_text):
        now = datetime.now(timezone.utc)
        rows = [{"session_id": self.session_id, "role": role, "content": content,
                 "created_at": (now + timedelta(microseconds=i)).isoformat()}
                for i, (role, content) in enumerate([("user", user_text), ("assistant", assistant_text)])]
        if self.client is not None and not self.persistence_error:
            try:
                self.client.table("jarvis_messages").insert(rows).execute()
            except Exception:
                self.persistence_error = True
        self._cache.extend({"role": row["role"], "content": row["content"]} for row in rows)
        self._cache = self._cache[-self.max_messages:]
