import streamlit as st
import pandas as pd
import numpy as np
import math

st.set_page_config(page_title="SPORT EDGE AI", page_icon="📊", layout="wide")
st.title("🏆 SPORT EDGE AI")
st.caption("Prototype 0.1 — analyse sportive, probabilités et comparaison de cotes")
st.warning("Les données de démonstration sont fictives. Cette version ne récupère pas les matchs ni les cotes en direct et ne garantit aucun gain.")

with st.sidebar:
    st.header("Configuration")
    sport = st.selectbox("Sport", ["Football", "Basketball"])
    mode = st.radio("Données", ["Démo fictive", "Importer mon CSV"])

def demo_data(sport):
    if sport == "Football":
        rows = [
            ["2025-08-10","Paris FC","Lyon",1,1,2.65,3.15,2.70],
            ["2025-08-17","Lyon","Marseille",2,1,2.30,3.30,3.05],
            ["2025-08-24","Lille","Paris FC",2,0,1.75,3.55,4.80],
            ["2025-08-31","Marseille","Lille",1,2,2.05,3.40,3.60],
            ["2025-09-07","Paris FC","Marseille",0,2,3.20,3.20,2.25],
            ["2025-09-14","Lyon","Lille",1,1,2.20,3.15,3.40],
            ["2025-09-21","Marseille","Lyon",2,2,1.95,3.50,3.70],
            ["2025-09-28","Lille","Paris FC",1,0,1.85,3.40,4.30],
            ["2025-10-05","Paris FC","Lyon",0,1,3.00,3.25,2.40],
            ["2025-10-12","Lille","Marseille",1,1,2.50,3.25,2.75],
            ["2025-10-19","Lyon","Paris FC",3,0,1.60,3.80,5.40],
            ["2025-10-26","Marseille","Paris FC",2,0,1.55,4.00,5.80],
        ]
        return pd.DataFrame(rows, columns=["date","home_team","away_team","home_score","away_score","home_odds","draw_odds","away_odds"])
    rows = [
        ["2025-10-01","Lions","Wolves",108,101,1.70,np.nan,2.25],
        ["2025-10-03","Wolves","Bears",99,104,2.10,np.nan,1.80],
        ["2025-10-05","Bears","Lions",112,109,2.05,np.nan,1.85],
        ["2025-10-07","Lions","Bears",115,103,1.65,np.nan,2.30],
        ["2025-10-09","Wolves","Lions",102,110,2.45,np.nan,1.55],
        ["2025-10-11","Bears","Wolves",107,100,1.75,np.nan,2.15],
        ["2025-10-13","Lions","Wolves",111,106,1.60,np.nan,2.40],
        ["2025-10-15","Bears","Lions",103,105,2.20,np.nan,1.70],
    ]
    return pd.DataFrame(rows, columns=["date","home_team","away_team","home_score","away_score","home_odds","draw_odds","away_odds"])

if mode == "Démo fictive":
    df = demo_data(sport)
    st.info("Mode démo : équipes, scores et cotes sont inventés.")
else:
    uploaded = st.file_uploader("Importer un CSV", type=["csv"])
    if uploaded is None:
        st.markdown("### Format CSV attendu")
        st.code("date,home_team,away_team,home_score,away_score,home_odds,draw_odds,away_odds\\n2025-01-01,Team A,Team B,2,1,1.90,3.40,4.20")
        st.stop()
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Impossible de lire le CSV : {e}")
        st.stop()

required = ["home_team", "away_team", "home_score", "away_score"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error("Colonnes obligatoires manquantes : " + ", ".join(missing))
    st.stop()
for c in ["home_score","away_score","home_odds","draw_odds","away_odds"]:
    if c not in df.columns:
        df[c] = np.nan
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df.dropna(subset=["home_team","away_team","home_score","away_score"])
if len(df) < 4:
    st.error("Il faut au moins 4 matchs historiques valides.")
    st.stop()

def poisson(k, lam):
    return math.exp(-lam) * lam**k / math.factorial(k)

def get_stats(data):
    avg_h = max(float(data.home_score.mean()), .1)
    avg_a = max(float(data.away_score.mean()), .1)
    league_avg = max((avg_h + avg_a) / 2, .1)
    stats = {}
    for team in sorted(set(data.home_team.astype(str)) | set(data.away_team.astype(str))):
        h = data[data.home_team.astype(str) == team]
        a = data[data.away_team.astype(str) == team]
        gf = h.home_score.sum() + a.away_score.sum()
        ga = h.away_score.sum() + a.home_score.sum()
        n = len(h) + len(a)
        stats[team] = {"matches": n, "gf": (gf + league_avg*4)/(n+4), "ga": (ga + league_avg*4)/(n+4)}
    return stats, avg_h, avg_a

def outcomes(lh, la):
    ph = [poisson(i, max(lh,.05)) for i in range(11)]
    pa = [poisson(i, max(la,.05)) for i in range(11)]
    h = d = a = 0
    for i in range(11):
        for j in range(11):
            p = ph[i]*pa[j]
            if i > j: h += p
            elif i == j: d += p
            else: a += p
    s = h+d+a
    return h/s, d/s, a/s

stats, avg_h, avg_a = get_stats(df)
teams = sorted(stats)
c1,c2,c3,c4 = st.columns(4)
c1.metric("Matchs chargés", len(df))
c2.metric("Équipes détectées", len(teams))
c3.metric("Moyenne domicile", f"{df.home_score.mean():.2f}")
c4.metric("Moyenne extérieur", f"{df.away_score.mean():.2f}")
with st.expander("Voir les données"):
    st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Analyser une rencontre")
c1,c2 = st.columns(2)
with c1: home = st.selectbox("Équipe à domicile", teams, index=0)
with c2: away = st.selectbox("Équipe à l'extérieur", [x for x in teams if x != home], index=0)

if sport == "Football":
    lh = max(.1, avg_h * (stats[home]["gf"]/avg_h) * (stats[away]["ga"]/avg_h))
    la = max(.1, avg_a * (stats[away]["gf"]/avg_a) * (stats[home]["ga"]/avg_a))
    p_home,p_draw,p_away = outcomes(lh,la)
    x1,x2,x3 = st.columns(3)
    x1.metric("Victoire domicile", f"{p_home*100:.1f}%")
    x2.metric("Match nul", f"{p_draw*100:.1f}%")
    x3.metric("Victoire extérieur", f"{p_away*100:.1f}%")
    st.caption(f"Buts attendus indicatifs : {lh:.2f} – {la:.2f}")
else:
    eh = (stats[home]["gf"] + stats[away]["ga"])/2
    ea = (stats[away]["gf"] + stats[home]["ga"])/2
    sd = max(float((df.home_score-df.away_score).std()), 8)
    z = (eh-ea)/sd
    p_home = .5*(1+math.erf(z/math.sqrt(2)))
    p_away = 1-p_home
    x1,x2,x3 = st.columns(3)
    x1.metric("Victoire domicile", f"{p_home*100:.1f}%")
    x2.metric("Écart estimé", f"{eh-ea:+.1f} points")
    x3.metric("Victoire extérieur", f"{p_away*100:.1f}%")
    st.caption(f"Score indicatif estimé : {eh:.1f} – {ea:.1f}")

st.subheader("Comparer aux cotes")
st.write("Entre les cotes décimales réellement disponibles.")
x1,x2,x3 = st.columns(3)
with x1: odd_h = st.number_input("Cote domicile", min_value=0.0, value=0.0, step=.05)
with x2: odd_d = st.number_input("Cote nul (football)", min_value=0.0, value=0.0, step=.05) if sport == "Football" else 0.0
with x3: odd_a = st.number_input("Cote extérieur", min_value=0.0, value=0.0, step=.05)
rows = [("Domicile",p_home,odd_h)]
if sport == "Football": rows.append(("Nul",p_draw,odd_d))
rows.append(("Extérieur",p_away,odd_a))
result = []
for name,prob,odd in rows:
    if odd > 1:
        result.append({"Marché":name,"Probabilité modèle":f"{prob*100:.1f}%","Probabilité brute cote":f"{100/odd:.1f}%","Valeur théorique":f"{(prob*odd-1)*100:+.1f}%","Cote":odd})
if result:
    st.dataframe(pd.DataFrame(result), use_container_width=True, hide_index=True)
    best = max((prob*odd-1 for _,prob,odd in rows if odd > 1), default=-1)
    if best >= .05:
        st.info("Écart théorique positif : à vérifier. Ce n'est pas un signal validé ni une garantie.")
    else:
        st.info("Aucun signal ne dépasse le seuil exploratoire de 5 %.")
else:
    st.caption("Saisis au moins une cote supérieure à 1 pour effectuer la comparaison.")

st.subheader("Historique des équipes")
team_df = pd.DataFrame([{"Équipe":t,"Matchs":stats[t]["matches"],"Buts pour lissés":round(stats[t]["gf"],2),"Buts contre lissés":round(stats[t]["ga"],2)} for t in teams])
st.dataframe(team_df.sort_values("Matchs",ascending=False), use_container_width=True, hide_index=True)
st.markdown("---")
st.caption("Prototype : modèles de base, pas encore validés hors échantillon. Pas de données en direct ni de paris automatiques. Utilise uniquement des données dont la licence autorise l'usage souhaité.")
