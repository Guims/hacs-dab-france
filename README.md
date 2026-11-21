# DAB+ France — carte HACS

**Version 0.5.1 (branche main)**

Carte Lovelace pour écouter les flux Internet des radios DAB+ françaises, sans tuner physique.

## Installation

Ajouter `https://github.com/Guims/hacs-dab-france` dans HACS, dépôts personnalisés, catégorie Tableau de bord. Télécharger puis ajouter une carte manuelle :

```yaml
type: custom:dab-france-card
```

Pour mettre à jour : retélécharger main dans HACS, puis actualiser le navigateur (Ctrl+F5).

## Fonctionnalités

- Recherche, filtres région et genre, favoris et logos.
- Lecture navigateur ou entité media_player, volume navigateur mémorisé localement.
- Alternatives de flux HTTPS dans le navigateur ; HLS selon compatibilité native.
- Égaliseur décoratif animé pendant la lecture.
- Titres et artistes : Icecast JSON, ICY, ou attributs du media_player externe.
- Actualisation des titres toutes les 25 secondes pendant la lecture locale.
- Cache local et catalogue de secours.

## Catalogue

Le fichier `catalog/stations.json` est chargé à distance. Le catalogue initial provient de [Ondes IDF](https://github.com/ekinox-ux/ondes-idf-catalogue), maintenu par ekinox-ux. Les ajouts régionaux sont recensés séparément et leurs flux recherchés notamment via Radio Browser. Le projet n'est pas affilié à ces services. Les droits sur les données, logos et flux restent à leurs titulaires ; la licence du catalogue amont reste à clarifier.

La couverture nationale est incomplète : Île-de-France, stations nationales et premiers ajouts d'Occitanie. Seules les stations avec un flux HTTPS marqué valide sont présentées. Un contrôle HTTP ne garantit pas la lecture sur chaque appareil.

## Maintenance

Le workflow [Vérification des radios](https://github.com/Guims/hacs-dab-france/actions) exécute `scripts/build_catalog.py` chaque nuit à 03h23 UTC. Il peut être lancé manuellement. Il vérifie les flux, tolère deux échecs successifs pour les flux précédemment valides, et publie le JSON. Le troisième échec les désactive. Aucun retéléchargement HACS n'est nécessaire pour une simple mise à jour du catalogue.

## Changelog

### 0.5.1
- Ignore les métadonnées sans lettres (identifiants numériques, notamment Nostalgie) et essaie les autres sources.
- Les titres intégralement numériques peuvent aussi être filtrés ; aucune résolution des identifiants propriétaires à ce stade.

### 0.5.0
- Module serveur facultatif ICY via WebSocket Home Assistant, sans URL fournie par le navigateur.
- Repli automatique sur ce module après échec des méthodes navigateur.
- Module indépendant disponible depuis la v0.5.1 ; non testé sur HAOS.

### 0.4.2
- Priorité à la dernière méthode de métadonnées ayant réussi pour le flux courant.
- Conservation du dernier titre pendant une panne temporaire, expiration après 90 secondes lors d'une vérification infructueuse.
- Version affichée dans la carte.
- Documentation actualisée.

### 0.4.1
- Lecture des métadonnées ICY, avec limite de durée et de volume de données.
- Annulation des requêtes lors des changements de station.

### 0.4.0
- Volume navigateur persistant, métadonnées Icecast JSON.
- Exploitation des flux directs régionaux et journalisation des contrôles.

### 0.3.1
- Filtres région et genre, workflow nocturne.
- Premiers ajouts régionaux et recherche Radio Browser.

### 0.3.0
- Catalogue hébergé dans le dépôt et script de contrôle.

### 0.2.0
- Catalogue Ondes IDF, cache et alternatives de flux.

### 0.1.0–0.1.1
- Première carte et catalogue de secours national.

## Limitations et suite

Les métadonnées navigateur dépendent de CORS et des informations réellement publiées par les radios. Les API spécifiques, les pochettes musicales dans le navigateur et l'égaliseur audio réel ne sont pas implémentés. La v0.5.0 n'a pas encore été testée dans Home Assistant. Les volumes des appareils externes ne sont pas restaurés automatiquement. Les favoris et réglages navigateur ne sont pas synchronisés entre appareils.

## Module serveur facultatif (expérimental)

Le module est désormais disponible dans un dépôt indépendant : [DAB+ France Metadata](https://github.com/Guims/hacs-dab-france-metadata), version 0.5.1.

Dans HACS, ajouter ce dépôt personnalisé dans la catégorie Intégration, télécharger main, redémarrer Home Assistant et ajouter DAB+ France Metadata dans Paramètres > Appareils et services. Aucun YAML nécessaire. Ne pas installer simultanément l'ancienne copie manuelle. La carte v0.5.0 détecte le module automatiquement lors de la recherche de titres. Recharger le tableau de bord après activation.

L'installation HACS et la lecture réelle restent à tester.
