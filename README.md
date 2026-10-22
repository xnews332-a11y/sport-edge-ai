# SPORT EDGE AI — Prototype 0.1

Prototype Streamlit pour analyser des données historiques importées en CSV.

## Lancer
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement gratuit
1. Crée un dépôt GitHub `sport-edge-ai`.
2. Ajoute `app.py`, `requirements.txt`, `README.md` et `sample_template.csv` à la racine.
3. Va sur https://share.streamlit.io, connecte GitHub, choisis le dépôt, la branche `main` et `app.py`, puis déploie.
4. Ouvre l'URL de l'application sur iPhone dans Safari et utilise Partager → Sur l'écran d'accueil.

## CSV
Colonnes obligatoires : `home_team`, `away_team`, `home_score`, `away_score`.
Colonnes facultatives : `date`, `home_odds`, `draw_odds`, `away_odds`.

Les données de démo sont fictives. Pas de récupération automatique des cotes en direct. Le modèle est un prototype non validé : il ne garantit pas de gains. Vérifie les licences et conditions d'utilisation des fournisseurs avant d'utiliser leurs données.
