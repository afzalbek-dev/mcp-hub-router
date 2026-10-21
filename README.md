# 🌐 MCP Hub Router

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Spec Compliant](https://img.shields.io/badge/MCP-2024--11--05-brightgreen.svg)]()

Anthropic tomonidan ishlab chiqilgan **Model Context Protocol (MCP)** spetsifikatsiyasiga to'liq mos keluvchi, AI agentlar (Claude Desktop, Cursor, Antigravity, LLM agentlar) uchun yengil vaznli vositalar shlyuzi (Tool Gateway), marshrutizator va telemetriya tizimi.

---

## 🌟 Imkoniyatlari

- **MCP Spetsifikatsiyasi:** `initialize`, `ping`, `tools/list`, `tools/call` kabi barcha standart JSON-RPC 2.0 protokollarini qo'llab-quvvatlaydi.
- **Qulay Dekorator:** Python funksiyalarini `@router.tool(...)` orqali bir zumda AI vositasiga aylantirish.
- **Asinxron va Sinxron:** Asinxron `async def` va sinxron `def` vositalarni bir xil marshrutlash.
- **Jonli Telemetriya (Router Telemetry):** Har bir vosita qancha millisekundda ishlagani, muvaffaqiyat foizi va xatoliklarni kuzatib boradi.
- **Zero-Dependency:** Tashqi og'ir paketlarsiz, Python standart kutubxonasida tez ishlaydi.

---

## 🚀 O'rnatish

```bash
git clone https://github.com/afzalbek-dev/mcp-hub-router.git
cd mcp-hub-router
pip install .
```

---

## 🛠️ Foydalanish

```python
import asyncio
from mcp_router import MCPRouter

router = MCPRouter(server_name="developer-toolkit", server_version="1.0.0")

# 1. AI agent uchun yangi instrument (tool) ro'yxatdan o'tkazish
@router.tool(
    name="get_weather_forecast",
    description="Berilgan shahar bo'yicha ob-havo ma'lumotini qaytaradi",
    input_schema={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "Shahar nomi (masalan: Tashkent)"}
        },
        "required": ["city"]
    }
)
async def weather_tool(city: str):
    return f"{city} shahrida havo ochiq, harorat +24°C"

# 2. JSON-RPC so'rovini qabul qilish va javob qaytarish
async def main():
    test_request = '''
    {
        "jsonrpc": "2.0",
        "id": "req-1",
        "method": "tools/call",
        "params": {
            "name": "get_weather_forecast",
            "arguments": {"city": "Tashkent"}
        }
    }
    '''
    response = await router.handle_request(test_request)
    print("MCP Javobi:", response)
    print("Telemetriya:", router.telemetry.summary())

asyncio.run(main())
```

---

## 🧪 Testlash

```bash
python3 -m unittest discover tests -v
```

---

## 📄 Litsenziya

MIT License. Muallif: [Afzalbek](https://github.com/afzalbek-dev).
