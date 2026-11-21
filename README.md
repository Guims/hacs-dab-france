# DAB+ France — carte HACS

Carte personnalisée Lovelace pour écouter les radios DAB+ françaises sur Home Assistant via leurs flux Internet. Aucun tuner physique nécessaire.

## Installation

Dans HACS, ajouter `https://github.com/Guims/hacs-dab-france` aux dépôts personnalisés (catégorie Tableau de bord), télécharger puis ajouter une carte manuelle :

```yaml
type: custom:dab-france-card
```

## Version 0.2.0

- Source principale : [Ondes IDF — catalogue](https://github.com/ekinox-ux/ondes-idf-catalogue), maintenu par ekinox-ux. Le JSON public est lu à distance lors du chargement ou d'une actualisation ; ne sont retenues que les stations ayant un bloc DAB+ et au moins un flux HTTPS marqué valide. Le catalogue n'est pas réédité ni republié dans ce dépôt.
- Cache du dernier catalogue dans le stockage du navigateur et sélection nationale minimale de secours si aucune synchronisation n'a encore réussi.
- Logos distants, recherche par nom, genre ou bloc, favoris locaux.
- Priorité aux flux directs MP3, alternatives HTTPS en cas d'échec de lecture dans le navigateur. Les lecteurs externes reçoivent le premier flux ; leurs capacités varient.
- Deux stations ne proposent que du HLS dans le catalogue du 20 novembre 2026 : un navigateur compatible HLS natif ou un lecteur externe compatible est nécessaire.
- Égaliseur décoratif, volume et sélection des entités media_player. Titres et pochettes selon les métadonnées fournies par le lecteur externe ; pas encore de récupération ICY dans le navigateur.

## Couverture

Le catalogue actuellement utilisé est francilien, incluant des radios nationales ; il ne couvre pas l'ensemble des régions de France. Le projet n'est pas affilié à Ondes IDF. Les flux et logos restent la propriété de leurs ayants droit. Le catalogue distant peut changer. Les données conservées localement restent propres à chaque navigateur.

## Développement

Version expérimentale : les flux marqués valides par la source n'ont pas été testés indépendamment dans Home Assistant.
