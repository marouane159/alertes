import streamlit as st
import requests
import time
import threading
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import os
from gtts import gTTS
import io
import json
import numpy as np
import base64 # Import the base64 library for encoding

# A list of Moroccan stocks with their symbols and sectors
BASE_STOCKS = [
    {"symbol": "TGC", "name": "TRAVAUX GENERAUX DE CONSTRUCTIONS", "sector": "Construction"},
    {"symbol": "TMA", "name": "TOTALENERGIES MARKETING MAROC", "sector": "Énergie"},
    {"symbol": "TQM", "name": "TAQA MOROCCO", "sector": "Énergie"},
    {"symbol": "NKL", "name": "ENNAKL SA", "sector": "Transport"},
    {"symbol": "LHM", "name": "LAFARGEHOLCIM", "sector": "Construction"},
    {"symbol": "UMR", "name": "UNIMER", "sector": "Agroalimentaire"},
    {"symbol": "WAA", "name": "WAFA ASSURANCE", "sector": "Assurance"},
    {"symbol": "ZDJ", "name": "ZELLIDJA S.A", "sector": "Mines"},
    {"symbol": "MSA", "name": "SODEP MARSA MAROC", "sector": "Transport"},
    {"symbol": "RDS", "name": "RESIDENCE DAR SAADA", "sector": "Construction"},
    {"symbol": "CSR", "name": "COSUMAR", "sector": "Industrie"},
    {"symbol": "CFG", "name": "CFG BANK", "sector": "Banque"},
    {"symbol": "CMG", "name": "CMGP CAS", "sector": "Agriculture"},
    {"symbol": "HPS", "name": "HPS", "sector": "Paiment"},
    {"symbol": "RIS", "name": "RISMA", "sector": "Hotel Management"},
    {"symbol": "DHO", "name": "DELTA HOLDING", "sector": "Industrie"},
    {"symbol": "DWY", "name": "DISWAY", "sector": "Distribution éléctro"},
    {"symbol": "SNA", "name": "STOKVIS NORD AFRIQUE", "sector": "Distribution service"},
    {"symbol": "SNP", "name": "SNEP", "sector": "Process Industries"},
    {"symbol": "STR", "name": "STROC INDUSTRIE", "sector": "Service Industriel"},
    {"symbol": "INV", "name": "INVOLYS", "sector": "Service de Technologie"},
    {"symbol": "MIC", "name": "MICRODATA", "sector": "Service de Technologie"},
    {"symbol": "DYT", "name": "DISTY TECHNOLOGIES", "sector": "Service de destribution"},
    {"symbol": "ADH", "name": "DOUJA PROM ADDOHA", "sector": "Immobilier"},
    {"symbol": "ADI", "name": "ALLIANCES", "sector": "Divers"},
    {"symbol": "AFI", "name": "AFRIC INDUSTRIES", "sector": "Industrie"},
    {"symbol": "AFM", "name": "AFMA", "sector": "Finance"},
    {"symbol": "AKT", "name": "AKDITAL S.A", "sector": "Santé"},
    {"symbol": "ALM", "name": "ALUMINIUM DU MAROC", "sector": "Matériaux"},
    {"symbol": "ARD", "name": "ARADEI CAPITAL", "sector": "Immobilier"},
    {"symbol": "ATH", "name": "AUTO HALL", "sector": "Automobile"},
    {"symbol": "ATL", "name": "ATLANTASANAD", "sector": "Distribution"},
    {"symbol": "ATW", "name": "ATTIJARIWAFA BANK", "sector": "Banque"},
    {"symbol": "BAL", "name": "BALIMA", "sector": "Distribution"},
    {"symbol": "BCP", "name": "BANQUE CENTRALE POPULAIRE", "sector": "Banque"},
    {"symbol": "CRS", "name": "CARTIER SAADA", "sector": "Distribution"},
    {"symbol": "CIH", "name": "CREDIT IMMOBILIER ET HOTELIER", "sector": "Banque"},
    {"symbol": "CMT", "name": "CIMENTS DU MAROC", "sector": "Matériaux"},
    {"symbol": "COL", "name": "COLORADO", "sector": "Distribution"},
    {"symbol": "CTM", "name": "COMPAGNIE DE TRANSPORTS AU MAROC", "sector": "Transport"},
    {"symbol": "DIM", "name": "DELATTRE LEVIVIER MAROC", "sector": "Industrie"},
    {"symbol": "DRI", "name": "DARI COUSPATE", "sector": "Agroalimentaire"},
    {"symbol": "EQD", "name": "EQDOM", "sector": "Immobilier"},
    {"symbol": "FBR", "name": "FENIE BROSSETTE", "sector": "Distribution"},
    {"symbol": "IAM", "name": "MAROC TELECOM", "sector": "Télécom"},
    {"symbol": "INM", "name": "INDUSTRIE DU MAROC", "sector": "Industrie"},
    {"symbol": "JET", "name": "JET CONTRACTORS", "sector": "Construction"},
    {"symbol": "LES", "name": "LESIEUR CRISTAL", "sector": "Agroalimentaire"},
    {"symbol": "MOX", "name": "MAGHREB OXYGENE", "sector": "Industrie"},
    {"symbol": "MNG", "name": "MANAGEM", "sector": "Mines"},
    {"symbol": "MUT", "name": "MUTANDIS", "sector": "Agroalimentaire"},
    {"symbol": "RDS", "name": "RÉSIDENCES DAR SAADA", "sector": "Immobilier"},
    {"symbol": "SID", "name": "SONASID", "sector": "Agroalimentaire"},
    {"symbol": "SNP", "name": "SNEP", "sector": "Industrie"},
    {"symbol": "SOT", "name": "SOTHEMA", "sector": "Pharma"},
    {"symbol": "SRM", "name": "REALISATIONS MECANIQUES", "sector": "Industrie"},
    {"symbol": "STR", "name": "STROC INDUSTRIE", "sector": "Industrie"},
    {"symbol": "MDP", "name": "MED PAPER", "sector": "Industrie"},
    {"symbol": "VCN", "name": "VICENNE", "sector": "Santé"},
    {"symbol": "SMI", "name": "Société métallurgique d'imiter", "sector": "Finance"},
    {"symbol": "CDM", "name": "Crédit du Maroc", "sector": "Banque"}
]

# Create a dictionary for quick lookup
STOCKS_DICT = {stock["symbol"]: stock for stock in BASE_STOCKS}

# --- Authentication Setup ---
ADMIN_USERNAME = "risk.maroc"
ADMIN_PASSWORD = "@risk.maroc"
PUBLIC_PASSWORD = "www.risk.ma"

def check_admin_credentials(username, password):
    """Check if the provided credentials match the admin credentials."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def check_public_password(password):
    """Check if the provided password matches the public access password."""
    return password == PUBLIC_PASSWORD

# --- Shared File Management Functions ---
def load_alerts():
    """Loads all alerts from the shared JSON file."""
    try:
        with open("alerts.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_alerts(alerts):
    """Saves all alerts to the shared JSON file."""
    with open("alerts.json", "w") as f:
        json.dump(alerts, f, indent=4)

def load_triggered_alerts():
    """Loads new triggered alerts from the temporary file."""
    triggered = []
    try:
        with open("triggered_alerts.json", "r") as f:
            for line in f:
                triggered.append(json.loads(line))
        # Clear the file after reading
        with open("triggered_alerts.json", "w") as f:
            f.write("")
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return triggered

# --- Helper Functions ---

def get_moroccan_stocks():
    """Scrapes stock data from TradingView."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        url = "https://www.tradingview.com/markets/stocks-morocco/market-movers-all-stocks/"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            return None
            
        stocks_data = []
        for row in table.find_all('tr')[1:]:
            try:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    symbol_cell = cells[0].find('a')
                    if symbol_cell:
                        symbol = symbol_cell.text.strip()
                        price_text = cells[1].text.strip()
                        
                        try:
                            price = float(price_text.replace('MAD', '').replace(',', '').strip())
                            stock_info = STOCKS_DICT.get(symbol)
                            if stock_info:
                                stocks_data.append({
                                    "symbol": symbol,
                                    "name": stock_info["name"],
                                    "price": price,
                                    "sector": stock_info["sector"]
                                })
                        except ValueError:
                            continue
            except Exception as e:
                continue
        
        return pd.DataFrame(stocks_data)
        
    except Exception as e:
        return None

def fetch_stock_price(stock_symbol):
    """Fetches the current price for a given stock symbol."""
    try:
        stocks_df = get_moroccan_stocks()
        if stocks_df is not None:
            stock_data = stocks_df[stocks_df['symbol'] == stock_symbol]
            if not stock_data.empty:
                return stock_data.iloc[0]['price']
        
        # Fallback to a mock price if scraping fails
        base_prices = {
            "ATL": 245.50, "AFI": 98.30, "ADI": 385.00, "ATW": 450.25,
            "BCP": 750.50, "CIH": 695.00, "IAM": 118.90, "ADH": 40.50,
        }
        return base_prices.get(stock_symbol, 100)
    except:
        return 100

def create_french_alert(stock_name, direction, target_price):
    """Generates a text-to-speech alert and returns it as a bytes buffer."""
    if direction == "above":
        text = f"Le titre {stock_name} est au dessus de {target_price} dirhams"
    elif direction == "below":
        text = f"Le titre {stock_name} est au dessous de {target_price} dirhams"
    else:  # equals
        text = f"Le titre {stock_name} est exactement à {target_price} dirhams"
    
    try:
        tts = gTTS(text=text, lang='fr')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        return None

def autoplay_audio(audio_buffer):
    """
    Plays an audio buffer automatically using an HTML audio tag.
    The audio player is hidden from view.
    """
    if audio_buffer:
        audio_bytes = audio_buffer.read()
        b64 = base64.b64encode(audio_bytes).decode()
        md = f"""
            <audio autoplay="true" style="display: none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# --- Background Thread Function ---

def check_alerts():
    """
    This function runs in a background thread to check for alerts.
    It's independent of any user session.
    """
    while True:
        try:
            # 1. Load the shared alerts from the file
            all_alerts = load_alerts()
            
            if not all_alerts:
                time.sleep(300)
                continue

            current_time = datetime.now()

            # Only check during market hours (9 AM to 4:30 PM)
            if current_time.hour >= 9 and current_time.hour < 16:
                for alert in all_alerts:
                    # Check if it's time to check this alert again
                    if 'last_checked' not in alert or current_time - datetime.fromisoformat(alert['last_checked']) >= timedelta(minutes=5):
                        current_price = fetch_stock_price(alert['symbol'])
                        alert['last_checked'] = current_time.isoformat()
                        
                        # Check if price target is reached
                        condition_met = False
                        if alert['direction'] == 'above' and current_price >= alert['target_price']:
                            condition_met = True
                        elif alert['direction'] == 'below' and current_price <= alert['target_price']:
                            condition_met = True
                        elif alert['direction'] == 'equals' and current_price == alert['target_price']:
                            condition_met = True
                        
                        if condition_met:
                            # 2. Write the triggered alert to a shared file
                            triggered_info = {
                                "name": alert['name'],
                                "price": current_price,
                                "target": alert['target_price'],
                                "direction": alert['direction'],
                                "timestamp": datetime.now().isoformat()
                            }
                            with open("triggered_alerts.json", "a") as f:
                                json.dump(triggered_info, f)
                                f.write("\n")
                            
                            # Remove the triggered alert from the active list
                            all_alerts.remove(alert)
                            save_alerts(all_alerts)
                            
            # 3. Save the updated alerts file (with last_checked times)
            save_alerts(all_alerts)
            
            # Wait for 5 minutes before the next check
            time.sleep(300)
        except Exception as e:
            time.sleep(60) # Wait a minute before retrying

# --- Initialize session state and start thread ---
if 'thread_started' not in st.session_state:
    st.session_state.thread_started = True
    thread = threading.Thread(target=check_alerts, daemon=True)
    thread.start()

# --- Authentication Section ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'public_access' not in st.session_state:
    st.session_state.public_access = False

# Display login form if not authenticated
if not st.session_state.authenticated and not st.session_state.public_access:
    st.title("Système d'Alertes Sonores des Cours | RISK NETWORK 🔔")
    
    # Admin login section
    with st.expander("Admin Login", expanded=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Admin Login"):
            if check_admin_credentials(username, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    # Public access section
    st.markdown("---")
    st.markdown("### Accès RISK NETWORK")
    public_password = st.text_input("Mot de passe RISK NETWORK", type="password")
    if st.button("Accéder aux alertes"):
        if check_public_password(public_password):
            st.session_state.public_access = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect. Accès réservé aux membres RISK NETWORK.")
    
    st.stop()

# --- Public View (RISK NETWORK Members) ---
if st.session_state.public_access:
    st.title("Système d'Alertes Sonores des Cours | RISK NETWORK 🔔")
    
    # Logout button for public access
    if st.sidebar.button("Se déconnecter (Public)"):
        st.session_state.public_access = False
        st.rerun()
    
    st.markdown("""
    ## Vue RISK NETWORK
    Cette application permet de visualiser les alertes boursières marocaines et d'écouter les alertes sonores.
    Accès réservé aux membres RISK NETWORK.
    """)
    
    # Display triggered alerts
    triggered_alerts = load_triggered_alerts()
    if triggered_alerts:
        st.header("🚨 Alertes Déclenchées")
        for alert in triggered_alerts:
            st.warning(f"{alert['name']} a atteint {alert['price']} MAD!")
            audio_buffer = create_french_alert(alert['name'], alert['direction'], alert['target'])
            autoplay_audio(audio_buffer)
    
    # Display current alerts
    current_alerts = load_alerts()
    if current_alerts:
        st.header("Alertes Actives")
        for alert in current_alerts:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader(alert['name'])
                st.caption(f"Symbole: {alert['symbol']}")
            
            with col2:
                if alert['direction'] == 'above':
                    direction_symbol = "↗️ Au-dessus de"
                elif alert['direction'] == 'below':
                    direction_symbol = "↘️ En-dessous de"
                else:
                    direction_symbol = "= Égal à"
                    
                st.write(f"**Prix Cible:** {alert['target_price']} MAD {direction_symbol}")
            
            st.divider()
    else:
        st.info("Aucune alerte active.")
    
    # Display current market data
    st.header("Données de Marché Actuelles")
    stocks_df = get_moroccan_stocks()
    if stocks_df is not None:
        st.dataframe(stocks_df[['symbol', 'name', 'price', 'sector']])
    else:
        st.error("Impossible de récupérer les données de marché actuelles.")
    
    # Display last update time
    st.caption(f"Dernière vérification des prix: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Les prix sont mis à jour toutes les 5 minutes pendant les heures de marché (9:00-16:30)")
    
    # Add copyright in footer
    st.markdown("---")
    st.markdown("<div style='text-align: center;'>© 2025 <a href='https://www.risk.ma' target='_blank'>www.risk.ma</a> - Accès réservé aux membres RISK NETWORK</div>", unsafe_allow_html=True)
    
    st.stop()

# --- Admin View (Authenticated Users) ---
st.title("Système d'Alertes Sonores des Cours | RISK NETWORK 🔔 (Admin Mode)")
st.markdown("""
Vous êtes en mode administrateur. Vous pouvez ajouter, modifier et supprimer des alertes.
""")

# Logout button
if st.sidebar.button("Logout (Admin)"):
    st.session_state.authenticated = False
    st.rerun()

# Display New Alerts (The "Live" Part)
triggered_alerts = load_triggered_alerts()
if triggered_alerts:
    for alert in triggered_alerts:
        st.warning(f"🚨 ALERTE: Le titre {alert['name']} a atteint {alert['price']} MAD!")
        audio_buffer = create_french_alert(alert['name'], alert['direction'], alert['target'])
        autoplay_audio(audio_buffer)

# --- Sidebar for Adding New Alerts ---
with st.sidebar:
    st.header("Ajouter une Nouvelle Alerte")
    
    # Get current stock data
    stocks_df = get_moroccan_stocks()
    
    if stocks_df is not None and not stocks_df.empty:
        stock_options = [f"{row['symbol']} - {row['name']}" for _, row in stocks_df.iterrows()]
        selected_stock = st.selectbox("Sélectionner une Action", stock_options)
        
        symbol = selected_stock.split(" - ")[0]
        stock_info = STOCKS_DICT.get(symbol, {"name": symbol, "sector": "Unknown"})
        current_price = fetch_stock_price(symbol)
        
        st.info(f"Prix actuel: {current_price} MAD")
        
        target_price = st.number_input("Prix Cible (MAD)", min_value=0.0, value=round(current_price * 1.05, 2))
        
        direction = st.radio("Alerter lorsque le prix est:", ["au-dessus", "en-dessous", "égal à"])
        direction_map = {"au-dessus": "above", "en-dessous": "below", "égal à": "equals"}
        
        if st.button("Ajouter l'Alerte"):
            new_alert = {
                'name': stock_info["name"],
                'symbol': symbol,
                'target_price': target_price,
                'direction': direction_map[direction],
                'created_at': datetime.now().isoformat()
            }
            
            # Load, append, and save to the shared file
            all_alerts = load_alerts()
            all_alerts.append(new_alert)
            save_alerts(all_alerts)
            st.success(f"Alerte ajoutée pour {stock_info['name']} à {target_price} MAD")
    else:
        st.error("Impossible de récupérer les données boursières. Veuillez réessayer plus tard.")

# --- Main Content Area ---
st.header("Vos Alertes Actives")
current_alerts = load_alerts()

if current_alerts:
    for i, alert in enumerate(current_alerts):
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.subheader(alert['name'])
            st.caption(f"Symbole: {alert['symbol']}")
            st.caption(f"Créée le: {alert['created_at']}")
        
        with col2:
            if alert['direction'] == 'above':
                direction_symbol = "↗️ Au-dessus de"
            elif alert['direction'] == 'below':
                direction_symbol = "↘️ En-dessous de"
            else:
                direction_symbol = "= Égal à"
                
            st.write(f"**Prix Cible:** {alert['target_price']} MAD {direction_symbol}")
        
        with col3:
            if st.button("Supprimer", key=f"delete_{i}"):
                current_alerts.pop(i)
                save_alerts(current_alerts)
                st.rerun()
        
        st.divider()
else:
    st.info("Aucune alerte configurée. Ajoutez votre première alerte en utilisant la barre latérale!")

# Display current market data
st.header("Données de Marché Actuelles")
if stocks_df is not None:
    st.dataframe(stocks_df[['symbol', 'name', 'price', 'sector']])
else:
    st.error("Impossible de récupérer les données de marché actuelles.")

# Display last update time
st.caption(f"Dernière vérification des prix: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Les prix sont mis à jour toutes les 5 minutes pendant les heures de marché (9:30-15:40)")

# Add copyright in footer
st.markdown("---")
st.markdown("<div style='text-align: center;'>© 2025 <a href='https://www.risk.ma' target='_blank'>www.risk.ma</a></div>", unsafe_allow_html=True)
