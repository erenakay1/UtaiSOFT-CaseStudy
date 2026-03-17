"""Database tool — SQLite."""

from __future__ import annotations

import sqlite3
from typing import Type

from pydantic import BaseModel, Field

import config
from registry.models import ToolMetadata
from tools.base import DynamicTool


def _init_db() -> None:
    """Create sample tables on first use."""
    conn = sqlite3.connect(str(config.SQLITE_DB_PATH))
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER,
            city TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL,
            category TEXT,
            stock INTEGER DEFAULT 0
        );

        -- Seed data (only if empty)
        INSERT OR IGNORE INTO users (id, name, email, age, city) VALUES
            (1, 'Ahmet Yılmaz', 'ahmet@example.com', 28, 'İstanbul'),
            (2, 'Elif Demir', 'elif@example.com', 34, 'Ankara'),
            (3, 'Mehmet Kaya', 'mehmet@example.com', 22, 'İzmir'),
            (4, 'Ayşe Çelik', 'ayse@example.com', 31, 'Bursa'),
            (5, 'Fatma Öz', 'fatma@example.com', 26, 'Antalya');

        INSERT OR IGNORE INTO products (id, name, price, category, stock) VALUES
            (1, 'Laptop', 25000.00, 'Elektronik', 15),
            (2, 'Kulaklık', 1500.00, 'Elektronik', 50),
            (3, 'Python Kitabı', 150.00, 'Kitap', 100),
            (4, 'Mekanik Klavye', 3000.00, 'Elektronik', 30),
            (5, 'AI Kursu', 500.00, 'Eğitim', 999);
        """
    )
    conn.commit()
    conn.close()


class DatabaseInput(BaseModel):
    query: str = Field(..., description="SQL query to execute (SELECT, INSERT, UPDATE, DELETE)")


class DatabaseTool(DynamicTool):
    name: str = "database"
    description: str = "Execute SQL queries on a SQLite database."
    args_schema: Type[BaseModel] = DatabaseInput

    def _run(self, query: str) -> str:
        try:
            _init_db()
            conn = sqlite3.connect(str(config.SQLITE_DB_PATH))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(query)
            query_upper = query.strip().upper()

            if query_upper.startswith("SELECT"):
                rows = cursor.fetchall()
                if not rows:
                    return "🗄 Sorgu sonucu: Kayıt bulunamadı."

                # Format as table
                columns = [desc[0] for desc in cursor.description]
                lines = [" | ".join(columns)]
                lines.append("-" * len(lines[0]))
                for row in rows:
                    lines.append(" | ".join(str(v) for v in row))

                conn.close()
                return f"🗄 Sorgu Sonucu ({len(rows)} kayıt):\n\n" + "\n".join(lines)

            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                return f"✅ Sorgu çalıştırıldı. Etkilenen satır: {affected}"

        except sqlite3.Error as e:
            return f"Veritabanı hatası: {e}"
        except Exception as e:
            return f"Beklenmeyen hata: {e}"

