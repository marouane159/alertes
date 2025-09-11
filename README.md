Here is a complete `README.md` description for your project, written in French, with the copyright link to `www.risk.ma`.

---

# Système d'Alertes Sonores Boursières | RISK NETWORK 🔔

Ce projet est une application Streamlit conçue pour fournir des alertes sonores en temps réel sur les prix des actions marocaines. Il est particulièrement utile pour les investisseurs et les traders qui souhaitent surveiller l'évolution des cours sans avoir à regarder constamment leur écran.

## Fonctionnalités Principales

* **Alertes en Temps Réel** : Le système vérifie les prix du marché toutes les 5 minutes et déclenche une alerte sonore dès qu'une condition de prix est atteinte (au-dessus, en-dessous ou égale à un prix cible).
* **Synthèse Vocale (gTTS)** : Les alertes sont transformées en messages audio clairs, annonçant le nom de l'action et le prix qui a déclenché l'alerte.
* **Accès Sécurisé** : L'application dispose d'un système de connexion par mot de passe pour les membres de **RISK NETWORK**, ainsi qu'un accès administrateur pour la gestion des alertes.
* **Interface Intuitive** : Une interface utilisateur simple et efficace, développée avec Streamlit, permet de visualiser les alertes actives et de consulter les données de marché en direct.

## Comment ça Marche ?

L'application est construite autour de plusieurs composants clés :

1.  **Web Scraping** : Le script utilise `requests` et `BeautifulSoup` pour extraire les données en temps réel des actions marocaines depuis TradingView.
2.  **Gestion des Alertes** : Les alertes sont sauvegardées dans un fichier `alerts.json`, permettant au système de les surveiller en continu.
3.  **Thread d'arrière-plan** : Un thread distinct s'exécute en permanence pour vérifier les prix des actions, indépendamment de l'interface utilisateur, garantissant que les alertes sont toujours surveillées.
4.  **Lecture Audio** : Lorsqu'une alerte est déclenchée, une phrase est générée avec `gTTS` et lue automatiquement grâce à l'intégration d'un lecteur audio HTML.


## Contact

Pour toute question ou demande de renseignements, veuillez visiter notre site web : [www.risk.ma](https://www.risk.ma).
Email: marouane@risk.ma

---
© 2025 [www.risk.ma](https://www.risk.ma)
