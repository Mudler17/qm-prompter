import textwrap
import streamlit as st
from datetime import date
import uuid
import streamlit.components.v1 as components

st.set_page_config(page_title="QM Promptbuilder (QMB)", page_icon="✅", layout="wide")

# -------- Sticky-Hinweis (oben, sehr sichtbar) --------
st.markdown(
    """
    <style>
      .sticky-banner{
        position: sticky;
        top: 0; z-index: 9999;
        padding: 10px 14px;
        border-left: 8px solid #d97706;
        background: #FEF3C7; /* amber-100 */
        color: #111827;
        font-weight: 600;
        border-radius: 6px;
        margin-bottom: 8px;
      }
      .sticky-banner small{font-weight: 500; color:#6b7280;}
    </style>
    <div class="sticky-banner">
      ⚠️ Datenschutz-Hinweis: <u>Keine personenbezogenen Daten</u> oder <u>internen Unternehmensdaten</u> eingeben.
      <small>Nur generische/abstrahierte Informationen verwenden.</small>
    </div>
    """,
    unsafe_allow_html=True
)

# -------- Helpers --------
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

def copy_to_clipboard_button(text: str, label: str = "📋 In Zwischenablage kopieren"):
    """
    Rendert einen HTML-Button, der den übergebenen Text in die Zwischenablage kopiert.
    Nutzt navigator.clipboard.writeText; benötigt https (Streamlit Cloud erfüllt das).
    """
    element_id = f"clip_{uuid.uuid4().hex}"
    escaped = (
        text.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("$", "\\$")
            .replace("</", "<\\/")
    )
    html = f"""
    <textarea id="{element_id}" style="position:absolute; left:-10000px; top:-10000px;">{escaped}</textarea>
    <button onclick="
        const el = document.getElementById('{element_id}');
        el.select();
        el.setSelectionRange(0, 999999);
        navigator.clipboard.writeText(el.value).then(() => {{
            const prev = this.innerText;
            this.innerText = '✅ Kopiert';
            setTimeout(() => this.innerText = prev, 1500);
        }}).catch(() => {{
            alert('Kopieren nicht möglich. Bitte manuell markieren und kopieren.');
        }});
    " style="
        cursor:pointer; padding:8px 12px; border-radius:6px;
        border:1px solid #D1D5DB; background:#F3F4F6;
    ">{label}</button>
    """
    components.html(html, height=0, scrolling=False)

# -------- Prompt-Templates --------
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

# Bereich -> empfohlene Use Cases
BEREICH_TO_TEMPLATES = {
    "Auditmanagement": ["Audit vorbereiten", "Management-Review", "Dokumentenprüfung/Lenkung"],
    "Risiko- & Chancenmanagement": ["Risikoanalyse (6.1)", "Kennzahlen/KPI-Board", "Management-Review"],
    "Beschwerdemanagement": ["Beschwerdemanagement", "Maßnahmenverfolgung (KVP)", "Kennzahlen/KPI-Board"],
    "Dokumentenlenkung": ["Dokumentenprüfung/Lenkung", "Prozessbeschreibung", "Management-Review"],
    "Prozessmanagement": ["Prozessbeschreibung", "Audit vorbereiten", "Kennzahlen/KPI-Board"],
    "Ziel- & Maßnahmenplanung": ["Maßnahmenverfolgung (KVP)", "Management-Review", "Kennzahlen/KPI-Board"],
    "Wissensmanagement": ["Schulung & Bewusstsein", "Dokumentenprüfung/Lenkung", "Management-Review"],
}

# Normen-Kacheln je Bereich
NORMVORSCHLAG = {
    "Auditmanagement": ["ISO 9001:2015, 9 Leistung/Evaluierung", "ISO 9001:2015, 10 Verbesserung"],
    "Risiko- & Chancenmanagement": ["ISO 9001:2015, 6.1 Risiken/Chancen", "ISO 9001:2015, 9 Leistung/Evaluierung"],
    "Beschwerdemanagement": ["ISO 9001:2015, 9 Leistung/Evaluierung", "ISO 9001:2015, 8 Betrieb"],
    "Dokumentenlenkung": ["ISO 9001:2015, 7 Unterstützung", "ISO 9001:2015, 8 Betrieb"],
    "Prozessmanagement": ["ISO 9001:2015, 4 Kontext", "ISO 9001:2015, 8 Betrieb"],
    "Ziel- & Maßnahmenplanung": ["ISO 9001:2015, 6.1 Risiken/Chancen", "ISO 9001:2015, 10 Verbesserung"],
    "Wissensmanagement": ["ISO 9001:2015, 7 Unterstützung", "ISO 9001:2015, 5 Führung"],
}
ALLE_NORMEN = sorted({n for lst in NORMVORSCHLAG.values() for n in lst})

# Beteiligte-Vorschläge je Use Case
BETEILIGTE_SUGGEST = {
    "Audit vorbereiten": ["QMB", "Prozessverantwortliche", "Leitung", "Auditor:in"],
    "Risikoanalyse (6.1)": ["Leitung", "Team", "QMB"],
    "Beschwerdemanagement": ["QMB", "Teamleitung", "Beschwerdebeauftragte:r", "Datenschutz"],
    "Dokumentenprüfung/Lenkung": ["Dokumenteigner:in", "QMB", "Freigabeinstanz"],
    "Maßnahmenverfolgung (KVP)": ["Owner", "QMB", "Leitung"],
    "Prozessbeschreibung": ["Prozessverantwortliche", "QMB", "Schnittstellenpartner"],
    "Management-Review": ["Geschäftsführung", "QMB", "Leitungen"],
    "Lieferantenbewertung": ["Einkauf", "QMB", "Fachbereich"],
    "Schulung & Bewusstsein": ["QMB", "HR/PE", "Fachcoaches"],
    "Kennzahlen/KPI-Board": ["QMB", "Leitung", "Controller:in"],
}

# KPI-Vorschläge je Use Case
KPI_SUGGEST = {
    "Audit vorbereiten": ["Auditabweichungen", "Termintreue Maßnahmen"],
    "Risikoanalyse (6.1)": ["Risikoprioritätszahl", "Eintretenshäufigkeit"],
    "Beschwerdemanagement": ["Bearbeitungszeit", "Wiederholrate", "Schweregrad-Score"],
    "Dokumentenprüfung/Lenkung": ["Aktualitätsquote", "Durchlaufzeit Revision"],
    "Maßnahmenverfolgung (KVP)": ["Umsetzungsgrad", "Wirksamkeitsquote"],
    "Prozessbeschreibung": ["Durchlaufzeit", "Fehlerquote", "Erstlösungsrate"],
    "Management-Review": ["Zielerreichung %", "Abweichungen ggü. Vorjahr"],
    "Lieferantenbewertung": ["Termintreue", "Beanstandungsquote"],
    "Schulung & Bewusstsein": ["Teilnahmequote", "Kompetenzcheck-Bestehensrate"],
    "Kennzahlen/KPI-Board": ["On-time Reporting", "KPI-Erfüllungsgrad"],
}

DATENSCHUTZ_HINT = {
    "Audit vorbereiten": "gering",
    "Risikoanalyse (6.1)": "gering",
    "Beschwerdemanagement": "hoch",
    "Dokumentenprüfung/Lenkung": "gering",
    "Maßnahmenverfolgung (KVP)": "gering",
    "Prozessbeschreibung": "keine",
    "Management-Review": "gering",
    "Lieferantenbewertung": "gering",
    "Schulung & Bewusstsein": "keine",
    "Kennzahlen/KPI-Board": "gering",
}

# -------- Sidebar: Modus & Export --------
with st.sidebar:
    st.header("⚙️ Modus & Export")
    modus = st.radio("Modus wählen", ["Geführt (empfohlen)", "Frei"], index=0)
    st.markdown("---")
    st.write("**Export**")
    filename = st.text_input("Dateiname (ohne Endung)", value="qm-prompt")
    add_context_header = st.checkbox("Metadaten als Kopfzeile einfügen", value=True)

st.title("✅ QM Promptbuilder (QMB)")
st.caption("Abhängige Dropdowns & geführte Menüführung für den Alltag des/der QMB.")

# -------- UI: Geführter Modus --------
if modus.startswith("Geführt"):
    st.subheader("1) Auswahl · Bereich → Use Case")
    colA, colB = st.columns([1, 1])

    with colA:
        bereich = st.selectbox(
            "Bereich",
            list(BEREICH_TO_TEMPLATES.keys()),
            index=0,
            help="Wähle zuerst den QM-Bereich. Die Use Cases passen sich automatisch an."
        )
    with colB:
        vorgeschlagene = BEREICH_TO_TEMPLATES[bereich]
        selected_template = st.selectbox(
            "Use Case",
            vorgeschlagene + [t for t in TEMPLATES.keys() if t not in vorgeschlagene],
            index=0,
            help="Priorisierte Vorschläge zuerst, weitere Use Cases darunter."
        )

    st.subheader("2) Kontext & Metadaten (vorausgefüllt, anpassbar)")
    col1, col2, col3 = st.columns([1.1, 1, 1])

    with col1:
        role = st.text_input("Rolle", value="Qualitätsmanagementbeauftragte:r (QMB)")
        norm_default = NORMVORSCHLAG.get(bereich, [])
        norm = st.multiselect("Normbezug (empfohlen)", ALLE_NORMEN, default=norm_default)

    with col2:
        beteiligte_default = BETEILIGTE_SUGGEST.get(selected_template, ["QMB", "Leitung"])
        beteiligte = st.multiselect("Beteiligte/Stakeholder", beteiligte_default, default=beteiligte_default)
        ressourcen = st.text_input("Ressourcen/Tools", value="Vorlagen, Planner/Boards, DMS, Risikomatrix")

    with col3:
        kpi_default = KPI_SUGGEST.get(selected_template, [])
        kpis = st.multiselect("KPIs/Kriterien (empfohlen)", kpi_default, default=kpi_default)
        schutz_default = DATENSCHUTZ_HINT.get(selected_template, "keine")
        schutz = st.selectbox("Datenschutzrelevanz", ["keine", "gering", "hoch"], index=["keine","gering","hoch"].index(schutz_default))
        frist = st.text_input("Frist/Zeitrahmen (optional)", value="")

    st.markdown("### 🧠 Kurzkontext")
    kontext = st.text_area(
        "Besonderheiten / Scope (z. B. Standort, Prozess, Stichprobe, bekannte Probleme)",
        height=120,
        placeholder="Kurzer, präziser Kontext. Beispiel: Internes Audit Prozess Aufnahmeverfahren, Fokus: Nachweise, Stichprobe: 10 Akten (Jan–März)."
    )

    st.markdown("### 📌 Ausgabepräferenz")
    stil = st.selectbox("Stil/Format", ["kühl & präzise", "praxisnah & knapp", "tabellarisch", "Checklistenstil"], index=2)

    st.markdown("---")
    generate_clicked = st.button("🎯 Prompt generieren", type="primary")

# -------- UI: Freier Modus --------
else:
    st.subheader("Freier Modus")
    col1, col2, col3 = st.columns([1.1, 1, 1])

    with col1:
        role = st.text_input("Rolle", value="Qualitätsmanagementbeauftragte:r (QMB)")
        bereich = st.selectbox("Bereich", list(BEREICH_TO_TEMPLATES.keys()), index=0)
        selected_template = st.selectbox("Vorlage/Use Case", list(TEMPLATES.keys()))

    with col2:
        norm = st.multiselect("Normbezug (optional)", ALLE_NORMEN, default=[])
        beteiligte = st.text_input("Beteiligte/Stakeholder (Komma-getrennt)", value="Leitung, Team, Träger")

    with col3:
        ressourcen = st.text_input("Ressourcen/Tools", value="Risikomatrix, Vorlagen, Planner/Boards, DMS")
        kpis = st.text_input("KPIs/Kriterien (optional)", value="Termintreue, Fehlerquote, Bearbeitungszeit")

    st.markdown("### 🧠 Kontext (frei)")
    kontext = st.text_area("Kurzbeschreibung / Besonderheiten / Scope", height=120)

    st.markdown("### 📌 Ausgabepräferenz")
    stil = st.selectbox("Stil/Format", ["kühl & präzise", "praxisnah & knapp", "tabellarisch", "Checklistenstil"], index=2)

    schutz = st.selectbox("Datenschutzrelevanz", ["keine", "gering", "hoch"], index=0)
    frist = st.text_input("Frist/Zeitrahmen (optional)", value="")

    st.markdown("---")
    generate_clicked = st.button("🎯 Prompt generieren", type="primary")

# -------- Prompt-Erstellung (beide Modi) --------
if generate_clicked:
    minimal_ok = bool(bereich and selected_template and role)
    if not minimal_ok:
        st.error("Bitte mindestens **Bereich, Use Case und Rolle** auswählen.")
    else:
        if isinstance(beteiligte, list):
            beteiligte_items = beteiligte
        else:
            beteiligte_items = [b.strip() for b in str(beteiligte).split(",") if b.strip()]

        if isinstance(kpis, list):
            kpi_items = kpis
        else:
            kpi_items = [k.strip() for k in str(kpis).split(",") if k.strip()]

        header = make_header(role, bereich, selected_template) if add_context_header else ""
        meta = "\n".join([
            bulletize("Norm", norm),
            bulletize("Beteiligte", beteiligte_items),
            bulletize("Ressourcen", [r.strip() for r in str(ressourcen).split(",")]),
            bulletize("KPIs/Kriterien", kpi_items),
            f"**Datenschutz:** {schutz}",
            f"**Frist:** {frist or '–'}",
            f"**Datum:** {date.today().isoformat()}",
        ])

        user_input = []
        if str(kontext).strip():
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
            instr += "\n**Bitte sachlich, präzise, normnah.**\n"

        prompt = nl_strip(header + "\n".join(user_input) + instr)

        st.success("Prompt erstellt. Du kannst ihn kopieren oder exportieren.")
        st.markdown("### ✅ Dein Prompt")
        st.code(prompt, language="markdown")

        # --- Neuer Button: In Zwischenablage kopieren ---
        copy_to_clipboard_button(prompt, "📋 In Zwischenablage kopieren")

        # --- Downloads: MD + TXT ---
        col_dl1, col_dl2 = st.columns([1,1])
        with col_dl1:
            st.download_button(
                label="⬇️ Als .md speichern",
                data=prompt.encode("utf-8"),
                file_name=f"{(filename or 'qm-prompt')}.md",
                mime="text/markdown",
            )
        with col_dl2:
            st.download_button(
                label="⬇️ Als .txt speichern",
                data=prompt,  # als String ok
                file_name=f"{(filename or 'qm-prompt')}.txt",
                mime="text/plain",
            )

# -------- Hilfe & Hinweise --------
with st.expander("ℹ️ Hinweise zur Menülogik & Datenschutz"):
    st.markdown("""
- **Geführter Modus:** Abhängige Dropdowns: *Bereich → Use Case → Normen/Beteiligte/KPIs* mit sinnvollen Defaults.
- **Datenschutz:** Die App ist für **abstrahierte Inhalte** konzipiert. Bitte **keine personenbezogenen** oder **internen** Daten eingeben.
- **Export:** Prompt als **Markdown** oder **Text** speichern. Zusätzlich: **Kopieren in Zwischenablage**.
""")
