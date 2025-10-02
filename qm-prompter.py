import textwrap
import streamlit as st
from datetime import date

st.set_page_config(page_title="QM Promptbuilder (QMB)", page_icon="✅", layout="wide")

# ---------- Helper ----------
def nl_strip(s: str) -> str:
    return textwrap.dedent(s).strip()

def section(title: str, body: str) -> str:
    body = body.strip()
    if not body:
        return ""
    return f"## {title}\n{body}\n"

def bulletize(label: str, items):
    items = [i for i in items if str(i).strip()]
    return f"**{label}:** " + (", ".join(items) if items else "–")

def make_header(role, bereich, auftrag):
    return f"# Rolle: {role} · Bereich: {bereich} · Auftrag: {auftrag}\n"

# ---------- Prompt-Templates ----------
TEMPLATES = {
    "Audit vorbereiten": nl_strip("""
    Du bist mein Co-Auditor. Erstelle auf Basis der Angaben eine **strukturierte Auditvorbereitung**:
    1) Auditfokus (Normstellen, Prozesse, Risiken/Chancen)
    2) **Fragenkatalog** (offen, nachweisorientiert), je Prozessschritt 3–5 Fragen
    3) **Nachweise** (Dokumente, Aufzeichnungen, Kennzahlen, Interviews, Beobachtungen)
    4) **Stichprobenplan** (Wie viele Fälle? Auswahlkriterien? Zeitraum?)
    5) **Risikohinweise** (typische Schwachstellen)
    6) **Datenschutz & Vertraulichkeit** (Hinweise für Audit)
    Ausgabe: kompakt, tabellarische Listen, klare Bulletpoints.
    """),
    "Risikoanalyse (6.1)": nl_strip("""
    Erzeuge eine **Risikobewertung** nach ISO 9001:2015, 6.1 mit:
    - Risiko-/Chancenliste (Kurzbeschreibung, Ursache, Auswirkung)
    - Bewertung (Eintrittswahrscheinlichkeit, Auswirkung, Risikopriorität)
    - **Maßnahmenplan** (SMART, Owner, Fällig bis, Wirksamkeitskriterium)
    - **Monitoring** (Review-Frequenz, Indikatoren/KPIs)
    Ausgabe: Tabelle + kurze Zusammenfassung (Top 3 Risiken mit Begründung).
    """),
    "Beschwerdemanagement": nl_strip("""
    Erstelle eine **strukturierte Auswertung** für Beschwerden:
    - Kategorisierung (Thema, Schweregrad, Betroffene)
    - **Root-Cause-Analyse** (5-Why/ISHIKAWA – komprimiert)
    - **Sofortmaßnahmen** vs. **Langfristmaßnahmen**
    - **Kommunikation** (an wen, wann, wie dokumentieren)
    - **Wirksamkeitsprüfung** (Kriterium, Zeitpunkt, Verantwortliche)
    Ausgabe: Kurzbericht + To-do-Liste.
    """),
    "Dokumentenprüfung/Lenkung": nl_strip("""
    Prüfe ein QM-Dokument (Versionierung, Gültigkeit, Freigabe, Verteilung):
    - **Checkliste** (Pflichtfelder, Normkonformität, Lesbarkeit)
    - **Änderungshistorie** (Was, warum, Folgen)
    - **Risiken bei Nichtaktualisierung**
    - **Empfehlung** (Freigeben, Überarbeiten, Archivieren) mit Begründung.
    Ausgabe: Entscheidungsvorlage (max. 1 Seite).
    """),
    "Maßnahmenverfolgung (KVP)": nl_strip("""
    Erstelle einen **KVP-Statusreport**:
    - Maßnahmenliste (Status, Hindernisse, nächste Schritte)
    - **Priorisierung** (Impact/Einfachheit)
    - **Escalation-Trigger** (Wann Leitung informieren?)
    - **Lerneffekte** (Was übernehmen wir als Standard?)
    Ausgabe: kompaktes Board (To Do / In Arbeit / Wirksamkeitsprüfung / Done).
    """),
    "Prozessbeschreibung": nl_strip("""
    Erstelle eine **Prozessbeschreibung**:
    - Zweck, Geltungsbereich, Schnittstellen
    - **Rollen & Verantwortlichkeiten (RACI)**
    - **Ablauf** in 5–9 Schritten (Input, Aktivität, Output, Nachweise)
    - **Kennzahlen/KPIs** (Definition, Messpunkt, Quelle)
    - **Risiken/Chancen** und Kontrollen
    Ausgabe: klare Struktur + 1 ASCII-Flussdiagramm.
    """),
    "Management-Review": nl_strip("""
    Struktur für ein **Management-Review**:
    - Zielerreichung, Ergebnisse interner/externer Audits
    - Prozessleistung/KPIs, Beschwerden/Stakeholder-Feedback
    - Ressourcen & Kompetenzen, Wirksamkeit von Maßnahmen
    - **Entscheidungen & Maßnahmen** (Strategie, Ziele, Ressourcen)
    Ausgabe: Agenda + Protokollgerüst (Beschluss/Owner/Termin).
    """),
    "Lieferantenbewertung": nl_strip("""
    Erstelle eine **Lieferantenbewertung**:
    - Kriterien (Qualität, Termintreue, Kommunikation, DSGVO/Ethik)
    - Punktesystem (1–5) + Gewichtungsvorschlag
    - **Maßnahmen je Kategorie** (A/B/C-Lieferant)
    - **Entwicklungsplan** (bei B/C) + Reviewzyklus.
    Ausgabe: Bewertungsmatrix + Kurzempfehlung.
    """),
    "Schulung & Bewusstsein": nl_strip("""
    Erstelle ein **Schulungskonzept** für QM-Grundlagen:
    - Zielgruppenanalyse (Bedarfe, Vorkenntnisse)
    - Lernziele, Inhalte, Methoden (Praxisfälle, Micro-Learning)
    - Nachweis (Teilnahme, Kompetenzcheck)
    - **Wirksamkeitsprüfung** (on-the-job Indikatoren)
    Ausgabe: 90-Min-Agenda + Materialliste.
    """),
    "Kennzahlen/KPI-Board": nl_strip("""
    Entwirf ein **KPI-Board**:
    - Auswahl geeigneter KPIs (Def., Formel, Zielwert, Quelle)
    - Visualisierungsempfehlung (Trend, Ampel)
    - **Reviewrhythmus** & Verantwortliche
    - **Interpretationsleitfaden** (Was tun bei Rot?).
    Ausgabe: tabellarisches Set + kurze Pflegehinweise.
    """),
}

NORMSTELLEN = [
    "ISO 9001:2015, 4 Kontext",
    "ISO 9001:2015, 5 Führung",
    "ISO 9001:2015, 6.1 Risiken/Chancen",
    "ISO 9001:2015, 7 Unterstützung",
    "ISO 9001:2015, 8 Betrieb",
    "ISO 9001:2015, 9 Leistung/Evaluierung",
    "ISO 9001:2015, 10 Verbesserung",
]

BEREICHE = [
    "Prozessmanagement",
    "Risiko- & Chancenmanagement",
    "Dokumentenlenkung",
    "Auditmanagement",
    "Beschwerdemanagement",
    "Ziel- & Maßnahmenplanung",
    "Wissensmanagement",
]

# ---------- UI ----------
with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.caption("QM-Promptbuilder für den Alltag des/der QMB")
    selected_template = st.selectbox("Vorlage/Use Case", list(TEMPLATES.keys()))
    st.markdown("---")
    st.write("**Export**")
    filename = st.text_input("Dateiname (ohne Endung)", value="qm-prompt")
    add_context_header = st.checkbox("Metadaten als Kopfzeile einfügen", value=True)

st.title("✅ QM Promptbuilder (QMB)")
st.write("Erzeuge in Sekunden **präzise Prompts** für wiederkehrende QM-Aufgaben. Kopieren oder als Datei exportieren.")

col1, col2, col3 = st.columns([1.1, 1, 1])

with col1:
    role = st.text_input("Rolle", value="Qualitätsmanagementbeauftragte:r (QMB)")
    bereich = st.selectbox("Bereich", BEREICHE, index=0)
    auftrag = st.text_input("Auftrag", value=selected_template)

with col2:
    norm = st.multiselect("Normbezug (optional)", NORMSTELLEN, default=[])
    beteiligte = st.text_input("Beteiligte/Stakeholder (Komma-getrennt)", value="Leitung, Team, Träger, ggf. Externe")
    ressourcen = st.text_input("Ressourcen/Tools", value="Risikomatrix, Vorlagen, Planner/Boards, DMS")

with col3:
    kpis = st.text_input("KPIs/Kriterien (optional)", value="Termintreue, Fehlerquote, Bearbeitungszeit")
    frist = st.text_input("Frist/Zeitrahmen (optional)", value="")
    schutz = st.selectbox("Datenschutzrelevanz", ["keine", "gering", "hoch"], index=0)

st.markdown("### 🧠 Kontext (frei formulierbar)")
kontext = st.text_area("Kurzbeschreibung / Besonderheiten / Scope", height=120, placeholder="z. B. Standort, Prozess, bekannte Probleme, Auditumfang …")

st.markdown("### 📌 Ausgabepräferenz")
stil = st.selectbox("Stil/Format", ["kühl & präzise", "praxisnah & knapp", "tabellarisch", "Checklistenstil"], index=2)

st.markdown("---")

if st.button("🎯 Prompt generieren", type="primary"):
    header = make_header(role, bereich, auftrag) if add_context_header else ""
    meta = "\n".join([
        bulletize("Norm", norm),
        bulletize("Beteiligte", [b.strip() for b in beteiligte.split(",")]),
        bulletize("Ressourcen", [r.strip() for r in ressourcen.split(",")]),
        bulletize("KPIs/Kriterien", [k.strip() for k in kpis.split(",")]),
        f"**Datenschutz:** {schutz}",
        f"**Frist:** {frist or '–'}",
        f"**Datum:** {date.today().isoformat()}",
    ])

    user_input = []
    if kontext.strip():
        user_input.append(section("Kontext", kontext))
    user_input.append(section("Metadaten", meta))

    instr = section("Auftrag an die KI", TEMPLATES[selected_template])
    if stil == "tabellarisch":
        instr += "\n**Bitte Tabellen überall dort, wo sinnvoll.**\n"
    elif stil == "Checklistenstil":
        instr += "\n**Bitte als Checklistenpunkte mit kurzen Begründungen.**\n"
    elif stil == "praxisnah & knapp":
        instr += "\n**Bitte knapp, mit Handlungsempfehlungen zuerst (Top-3).**\n"
    else:
        # kühl & präzise
        instr += "\n**Bitte sachlich, präzise, normnah.**\n"

    prompt = nl_strip(header + "\n".join(user_input) + instr)

    st.markdown("### ✅ Dein Prompt")
    st.code(prompt, language="markdown")

    st.download_button(
        label="⬇️ Als .md speichern",
        data=prompt.encode("utf-8"),
        file_name=f"{(filename or 'qm-prompt')}.md",
        mime="text/markdown",
    )

st.markdown("---")
with st.expander("📚 Prompt-Bibliothek (Sofort nutzbar)"):
    for key, val in TEMPLATES.items():
        st.markdown(f"**{key}**")
        st.code(val, language="markdown")
