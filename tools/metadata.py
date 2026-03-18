"""Tool Metadata Registry

Since LangChain BaseTool heavily manipulates class attributes via Pydantic metaclasses,
we define the metadata separately from the actual tool classes to avoid getting
our methods stripped.
"""

from registry.models import ToolMetadata

# Central dictionary holding all tool metadata
TOOL_METADATA_REGISTRY: dict[str, ToolMetadata] = {
    "weather": ToolMetadata(
        name="weather",
        display_name="Weather Information",
        description=(
            "Get real-time weather information for any city in the world. "
            "Returns temperature, humidity, wind speed, and weather conditions. "
            "Uses OpenWeatherMap API."
        ),
        parameters={
            "city": {"type": "string", "description": "City name"},
            "units": {"type": "string", "description": "metric/imperial/standard", "default": "metric"},
        },
        category="information",
        examples=[
            "İstanbul'da hava nasıl?",
            "What's the weather in London?",
            "Ankara hava durumu",
            "New York'ta sıcaklık kaç derece?",
            "Bugün hava yağmurlu mu?",
        ],
    ),
    "web_search": ToolMetadata(
        name="web_search",
        display_name="Web Search",
        description=(
            "Search the internet for up-to-date information on any topic. "
            "Returns relevant web pages with titles, URLs, and content snippets. "
            "Uses Tavily Search API."
        ),
        parameters={
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "description": "Number of results", "default": 5},
        },
        category="information",
        examples=[
            "Python 3.12 yeniliklerini ara",
            "En iyi yapay zeka kursları nelerdir?",
            "Search for latest news about AI",
            "LangChain nedir?",
            "2024 Oscar kazananları kim?",
        ],
    ),
    "currency": ToolMetadata(
        name="currency",
        display_name="Currency Converter",
        description=(
            "Convert between world currencies using real-time exchange rates. "
            "Supports all major currencies (USD, EUR, TRY, GBP, JPY, etc.). "
            "Uses ExchangeRate-API."
        ),
        parameters={
            "amount": {"type": "number", "description": "Amount to convert"},
            "from_currency": {"type": "string", "description": "Source currency code"},
            "to_currency": {"type": "string", "description": "Target currency code"},
        },
        category="utility",
        examples=[
            "100 dolar kaç TL?",
            "1 euro kaç lira?",
            "Convert 50 GBP to USD",
            "Döviz kuru nedir?",
            "500 TL kaç euro eder?",
        ],
    ),
    "translate": ToolMetadata(
        name="translate",
        display_name="Language Translator",
        description=(
            "Translate text between languages. Supports auto-detection of source language. "
            "Can translate to and from most world languages including Turkish, English, "
            "German, French, Spanish, Chinese, Japanese, Arabic, and many more."
        ),
        parameters={
            "text": {"type": "string", "description": "Text to translate"},
            "dest": {"type": "string", "description": "Target language code", "default": "tr"},
            "src": {"type": "string", "description": "Source language code", "default": "auto"},
        },
        category="utility",
        examples=[
            "Hello'yu Türkçe'ye çevir",
            "Translate 'Merhaba dünya' to English",
            "Bu cümleyi Almanca'ya çevir",
            "Comment dit-on bonjour en turc?",
            "'Günaydın' İngilizce ne demek?",
        ],
    ),
    "calendar": ToolMetadata(
        name="calendar",
        display_name="Google Calendar",
        description=(
            "Manage Google Calendar. List upcoming events or create new events. "
            "Shows event titles, dates, and times. Can schedule meetings, "
            "appointments, and reminders on Google Calendar."
        ),
        parameters={
            "action": {"type": "string", "description": "list | create"},
            "summary": {"type": "string", "description": "Event title"},
            "start_time": {"type": "string", "description": "ISO datetime"},
            "end_time": {"type": "string", "description": "ISO datetime"},
        },
        category="communication",
        examples=[
            "Bugünkü toplantılarımı göster",
            "Yarın saat 14:00'te bir toplantı oluştur",
            "Takvimimdeki etkinlikler neler?",
            "Show my upcoming events",
            "Schedule a meeting for tomorrow",
        ],
    ),
    "email": ToolMetadata(
        name="email",
        display_name="Gmail Email",
        description=(
            "Send and read emails through Gmail. Can compose and send new emails, "
            "and read recent emails from the inbox showing sender and subject."
        ),
        parameters={
            "action": {"type": "string", "description": "send | read"},
            "to": {"type": "string", "description": "Recipient address"},
            "subject": {"type": "string", "description": "Email subject"},
            "body": {"type": "string", "description": "Email body"},
        },
        category="communication",
        examples=[
            "Son e-postalarımı göster",
            "ali@example.com adresine bir e-posta gönder",
            "ali@example.com adresine bir mail gönder",
            "Gelen kutum ne durumda?",
            "Send an email to test@test.com",
            "Read my recent emails",
            "Mail at",                          
            "E-posta yolla",                    
        ],
    ),
    "document_reader": ToolMetadata(
        name="document_reader",
        display_name="Document Reader",
        description=(
            "Read and extract text from PDF and TXT documents. "
            "Supports both URLs and local file paths. "
            "Can parse multi-page PDFs and plain text files."
        ),
        parameters={
            "source": {"type": "string", "description": "URL or local path"},
            "max_chars": {"type": "integer", "description": "Max chars to return", "default": 3000},
        },
        category="information",
        examples=[
            "Bu PDF'yi oku: https://example.com/doc.pdf",
            "Şu dosyayı özetle: /path/to/file.txt",
            "Read this document",
            "PDF içeriğini göster",
            "Belgenin içinde ne yazıyor?",
        ],
    ),
    "database": ToolMetadata(
        name="database",
        display_name="SQL Database",
        description=(
            "Execute SQL queries on a SQLite database. "
            "Supports SELECT, INSERT, UPDATE, DELETE operations. "
            "Has sample tables: 'users' (name, email, age, city) and "
            "'products' (name, price, category, stock). "
            "Can query, insert, update, and delete data."
        ),
        parameters={
            "query": {"type": "string", "description": "SQL query to execute"},
        },
        category="utility",
        examples=[
            "Veritabanındaki tüm kullanıcıları göster",
            "SELECT * FROM products WHERE price > 1000",
            "Kaç tane ürün var?",
            "İstanbul'daki kullanıcıları listele",
            "Yeni bir kullanıcı ekle",
        ],
    ),
    "code_executor": ToolMetadata(
        name="code_executor",
        display_name="Python Code Executor",
        description=(
            "Execute Python code and return the printed output. "
            "Can perform mathematical calculations, data processing, "
            "algorithm execution, and any general Python computation. "
            "Supports standard modules like math, datetime, json, etc."
        ),
        parameters={
            "code": {"type": "string", "description": "Python code to execute"},
        },
        category="computation",
        examples=[
            "Python ile fibonacci hesapla",
            "2 + 2 kaç eder?",
            "Bir listeyi sırala",
            "Calculate factorial of 10",
            "Asal sayıları bul",
            "Bir fonksiyon yaz ve çalıştır",
        ],
    ),
    "timer": ToolMetadata(
        name="timer",
        display_name="Timer / Alarm",
        description=(
            "Set countdown timers and alarms. Can create timers with a specified "
            "duration in seconds, list all active timers, and cancel existing timers. "
            "Runs in the background and notifies when time is up."
        ),
        parameters={
            "action": {"type": "string", "description": "set | list | cancel"},
            "name": {"type": "string", "description": "Timer name"},
            "seconds": {"type": "integer", "description": "Duration in seconds"},
        },
        category="utility",
        examples=[
            "5 dakikalık bir timer kur",
            "30 saniye sonra hatırlat",
            "Set a 10 minute timer",
            "Aktif timer'ları göster",
            "Timer'ı iptal et",
        ],
    ),
    "ip_lookup": ToolMetadata(
        name="ip_lookup",
        display_name="IP Lookup",
        description=(
            "Look up geolocation, ISP, and network information for any IP address. "
            "Returns country, city, region, ISP name, organization, coordinates, "
            "and timezone. Can also detect the user's own public IP address."
        ),
        parameters={
            "ip": {"type": "string", "description": "IP address to look up (empty for own IP)", "default": ""},
        },
        category="information",
        examples=[
            "IP adresimi sorgula",
            "8.8.8.8 IP adresi kimin?",
            "Bu IP nerede: 1.1.1.1",
            "What is my IP address?",
            "IP adresinin lokasyonunu bul",
        ],
    ),
}

def get_tool_metadata(tool_name: str) -> ToolMetadata:
    if tool_name not in TOOL_METADATA_REGISTRY:
        raise ValueError(f"No metadata found for tool: {tool_name}")
    return TOOL_METADATA_REGISTRY[tool_name]
