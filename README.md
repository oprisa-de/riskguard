# RiskGuard: AI-Powered Portfolio Diversification Engine (RPDE)
## (Risiko-Management-System zur Portfolio-Diversifizierung)

---

## 🚀 Project Overview | Projektübersicht

**English:**
RiskGuard is an intelligent multi-agent system designed to solve one of the most critical challenges for growing businesses: **Concentration Risk**. Many companies inadvertently become over-dependent on a small number of high-revenue clients. RiskGuard analyzes client interaction patterns, identifies "success DNA," and provides an automated roadmap to diversify revenue streams while identifying "Danger Signals" like payment delays or declining engagement.

**Deutsch:**
RiskGuard ist ein intelligentes Multi-Agenten-System, das entwickelt wurde, um eine der kritischsten Herausforderungen für wachsende Unternehmen zu lösen: das **Konzentrationsrisiko**. Viele Unternehmen werden unbewusst zu abhängig von einer kleinen Anzahl von Großkunden. RiskGuard analysiert Kundeninteraktionsmuster, identifiziert „Erfolgs-DNA“ und bietet eine automatisierte Roadmap zur Diversifizierung von Umsatzströmen, während es gleichzeitig „Warnsignale“ wie Zahlungsverzug oder sinkendes Engagement erkennt.

---

## 🛠 Key Features | Kernfunktionen

| Feature | Description (EN) | Beschreibung (DE) |
| :--- | :--- | :--- |
| **Concentration Scoring** | Automatically detects when a client exceeds a specific % of total revenue. | Erkennt automatisch, wenn ein Kunde einen bestimmten Prozentsatz des Gesamtumsatzes überschreitet. |
| **Danger Signal Alerts** | Monitors for payment delays, erratic purchasing, and declining engagement. | Überwacht Zahlungsverzögerungen, unregelmäßige Bestellungen und sinkendes Engagement. |
| **Success DNA Profiling** | Identifies the behavior of high-performing clients to find similar opportunities in other industries. | Identifiziert das Verhalten erfolgreicher Kunden, um ähnliche Chancen in anderen Branchen zu finden. |
| **AI-Driven Roadmap** | Generates a step-by-step strategy to diversify the business portfolio. | Generiert eine schrittweise Strategie zur Diversifizierung des Geschäftsportfolios. |

---

## 🏗 Architecture & AI Tech Stack | Architektur & Technologie

RiskGuard leverages a **Hybrid AI Architecture** to balance privacy, cost, and high-level reasoning.

### **The Multi-Agent System (MAS)**
The system operates as a collaborative swarm of specialized agents:
1.  **The Profiler:** Analyzes historical data to identify successful client profiles.
2.  **The Market Scout:** Compares success patterns against other industries to find new markets.
3.  **The Project Architect:** Analyzes internal resources to build a diversification roadmap.

### **Technical Stack**
*   **Orchestration:** LangGraph & LangChain (for complex agentic workflows).
*   **LLMs:** 
    *   **Gemma 4 (Local):** Used for high-volume data processing, risk scoring, and privacy-sensitive analysis.
    *   **Claude 3.5 Sonnet (Online):** Used for high-level strategic reasoning and roadmap synthesis.
*   **Data Processing:** Pandas, NumPy, Scikit-learn.
*   **Backend:** Python 3.11.

---

## 🧪 How it Works | Funktionsweise

The system processes data in a three-stage pipeline:
1.  **Data Extraction:** Ingests client records (Revenue, Payment Status, Engagement Score).
2.  **Risk Assessment:** The **RiskEngine** calculates the "Concentration Score" and flags accounts that violate safety rules.
3.  **Strategic Synthesis:** The **Project Architect** uses LLMs to interpret the data and suggest specific, actionable steps to find new customers in other sectors.

---

## 🚀 Getting Started | Erste Schritte

To run the RiskGuard prototype locally:

```bash
# Clone the repository
git clone https://github.com/your-username/riskguard.git
cd riskguard

# Install dependencies
pip install -r requirements.txt

# Run the Phase 1 Analysis (Synthetic Data Demo)
python3 data/test_phase_1.py
```

---

## 👤 Author | Autor
**Mihai Oprisa**
*AI Engineer | Data Analyst*

---
*Disclaimer: This project uses synthetic data for demonstration purposes. No real-world client data is stored or processed in this repository.*
