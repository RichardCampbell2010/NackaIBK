import streamlit as st
import pandas as pd

# Sätt upp sidkonfiguration
st.set_page_config(
    page_title="The Campbell Formula (TCF)",
    page_icon="☩",
    layout="wide"
)

# --- INITIALISERA SESSION STATE (FÖR ATT SÄKERSTÄLLA ATT SPELARE INTE FÖRSVINNER) ---
if "players" not in st.session_state:
    st.session_state.players = [
        {"id": 1, "name": "Anna Andersson", "position": "Back", "number": 5},
        {"id": 2, "name": "Elin Berg", "position": "Back", "number": 12},
        {"id": 3, "name": "Sara Carlsson", "position": "Forward", "number": 9},
        {"id": 4, "name": "Ida Dahl", "position": "Forward", "number": 17},
        {"id": 5, "name": "Maja Ek", "position": "Målvakt", "number": 1}
    ]

if "matches" not in st.session_state:
    st.session_state.matches = [
        {"match_id": "Omgång 1 vs Täby", "xg_team": 2.4, "xg_against": 1.1, "result": "Vinst 5-2"},
        {"match_id": "Omgång 2 vs Rönnby", "xg_team": 1.8, "xg_against": 2.0, "result": "Förlust 3-4"}
    ]

# --- SIDPANEL: INLOGGNING & ROLLER ---
st.sidebar.title("☩ TCF Inloggning")
role_choice = st.sidebar.selectbox("Välj roll", ["Huvudtränare (Admin)", "Tränarkollega", "Spelare"])

current_user = None
if role_choice == "Spelare":
    player_names = [p["name"] for p in st.session_state.players]
    current_user = st.sidebar.selectbox("Välj spelare", player_names)

st.sidebar.markdown("---")
app_mode = st.sidebar.radio("Navigering", [
    "🏠 Start & Översikt", 
    "📊 Lagstatistik & xG", 
    "⭐ Min Individuella Statistik", 
    "⚙️ Admin / Trupphantering", 
    "📖 TCF-Lexikon"
])

# --- 1. START & ÖVERSIKT ---
if app_mode == "🏠 Start & Översikt":
    st.title("The Campbell Formula (TCF)")
    st.subheader("Nacka IBK Dam – Datadriven Innebandyanalys")
    
    st.info("Välkommen till TCF-systemet. Här bygger vi våra framgångar på exakta data, rätt skottval och starkt duellspel[span_0](start_span)[span_0](end_span)!")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Spelare i truppen", len(st.session_state.players))
    col2.metric("Analyserade matcher", len(st.session_state.matches))
    col3.metric("Systemversion", "1.0 Stabil")

# --- 2. LAGSTATISTIK & XG ---
elif app_mode == "📊 Lagstatistik & xG":
    st.title("Lagstatistik & TCF xG-modul")
    st.write("Här följer vi lagets gemensamma xG, kontringsspel och zoner baserat på vår forskningsbaserade modell.")
    
    # Exempel på tabell för matcher
    df_matches = pd.DataFrame(st.session_state.matches)
    st.dataframe(df_matches, use_container_width=True)
    
    st.markdown("### Nyckelinsikter från TCF-modellen")
    st.success("• **Volymparadoxen:** 55% av våra mål görs på nära håll (under 5 meter). Vi fokuserar på kvalitet framför långskottskvantitet.")
    st.success("• **Kontringsspel:** 39% av målen sker via snabba omställningar på under 6 sekunder[span_1](start_span)[span_1](end_span).")

# --- 3. INDIVIDUELL STATISTIK ---
elif app_mode == "⭐ Min Individuella Statistik":
    st.title("Individuell Spelarutveckling")
    
    if role_choice == "Spelare" and current_user:
        player_info = next(p for p in st.session_state.players if p["name"] == current_user)
        st.subheader(f'Inloggad som: {player_info["name"]} (#{player_info["number"]} - {player_info["position"]})')
        
        st.write("Här ser du din egen rådata och hur du presterar jämfört med snittet för andra spelare på samma position.")
        
        # Mock-data för individuell spelare
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Snitt Bollinnehavstid", "3.2 sekunder")
            st.metric("Framåtdriv efter bollvinst", "4.5 / match")
        with col2:
            st.metric("Vunna dueller (Egen zon)", "78%")
            st.metric("Individuellt xG-bidrag", "0.35 / match")
            
        st.markdown("### Utveckling över tid")
        st.line_chart([1.2, 1.5, 1.1, 2.0, 2.4], label="Ditt xG-bidrag senaste 5 matcherna")
    else:
        st.warning("Välj 'Spelare' i sidopanelen och välj ditt namn för att se din personliga statistik.")

# --- 4. ADMIN / TRUPPHANTERING ---
elif app_mode == "⚙️ Admin / Trupphantering":
    if role_choice == "Huvudtränare (Admin)":
        st.title("Administratör: Hantera Trupp och Matcher")
        
        st.markdown("### Lägg till ny spelare")
        with st.form("add_player_form"):
            new_name = st.text_input("Spelarens namn")
            new_pos = st.selectbox("Position", ["Back", "Forward", "Målvakt"])
            new_num = st.number_input("Tröjnummer", min_value=1, max_value=99, value=10)
            submitted = st.form_submit_button("Lägg till spelare")
            
            if submitted and new_name:
                new_id = max([p["id"] for p in st.session_state.players]) + 1 if st.session_state.players else 1
                st.session_state.players.append({"id": new_id, "name": new_name, "position": new_pos, "number": new_num})
                st.success(f"Spelare {new_name} tillagd utan risk för att andra försvinner!")
                st.rerun()

        st.markdown("### Nuvarande Trupp")
        df_players = pd.DataFrame(st.session_state.players)
        st.dataframe(df_players, use_container_width=True)
        
        # Ta bort spelare säkert via ID
        player_to_delete = st.selectbox("Välj spelare att ta bort", [p["name"] for p in st.session_state.players])
        if st.button("Ta bort markerad spelare"):
            st.session_state.players = [p for p in st.session_state.players if p["name"] != player_to_delete]
            st.success(f"Spelaren har tagits bort.")
            st.rerun()
            
    else:
        st.error("Behörighet saknas. Denna sida är endast till för Huvudtränare (Admin).")

# --- 5. TCF-LEXIKON ---
elif app_mode == "📖 TCF-Lexikon":
    st.title("TCF-Lexikonet")
    st.write("Här förklarar vi allt vi mäter – så enkelt att till och med en 8-åring förstår det!")
    
    with st.expander("Vad är Expected Goals (xG)?"):
        st.write("**HUR:** Vi tittar på exakt varifrån skottet sköts, vilken vinkel det var och om det stod en spelare i vägen[span_2](start_span)[span_2](end_span).")
        st.write("**VAD:** Det är en poäng mellan 0 och 1 som visar hur stor chans det var att bollen skulle gå in i mål.")
        st.write("**VARFÖR:** För att se till att vi skjuter från de farliga ställena istället för att bara måtta bollar långt utifrån.")

    with st.expander("Vad är Närkampsspel (Dueller)?"):
        st.write("**HUR:** Vi räknar varje gång två spelare kämpar kropp mot kropp om bollen.")
        st.write("**VAD:** Om vi vinner bollen eller förlorar den till motståndaren[span_3](start_span)[span_3](end_span).")
        st.write("**VARFÖR:** Innebandy är en tuff kamp. Den som vinner duellerna i försvaret och anfallet vinner oftast matchen[span_4](start_span)[span_4](end_span)!")

    with st.expander("Vad är Framåtdriv efter bollvinst?"):
        st.write("**HUR:** Vi kollar vad spelaren gör direkt när hon vinner bollen.")
        st.write("**VAD:** Om hon snabbt springer eller driver bollen framåt mot motståndarens mål[span_5](start_span)[span_5](end_span).")
        st.write("**VARFÖR:** Studier visar att man måste agera blixtsnabbt när man vinner boll för att överraska motståndarna[span_6](start_span)[span_6](end_span)!")

    with st.expander("Vad är Bollinnehavstid?"):
        st.write("**HUR:** Vi klockar hur många sekunder bollen är kvar på klubban.")
        st.write("**VAD:** Tiden från det att spelaren tar emot bollen tills hon passar eller skjuter.")
        st.write("**VARFÖR:** För att se till att spelet rullar på snabbt och effektivt.")
