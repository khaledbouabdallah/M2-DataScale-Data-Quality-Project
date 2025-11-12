![logo](../assets/images/uni_logo.jpeg)

# Projet Qualité des Données : ETL Consommation Énergétique

**M2 DataScale 2025/2026** | Zoubida Kedad  
**Équipe :** Khaled Bouabdallah, Théo Joly, Mohammed Nassim Fellah, Sarah Boundaoui  
**Dernière mise à jour :** 2025-11-11

---

## 1. Conception de Mapping: Approche Union-First

**Stratégie :** Fusionner les sources tôt, transformer une fois, séparer les sorties tard.

**Pipeline :**
```
S1 (Paris) + S2 (Évry) → Union → Transform → Split → Cibles
```

**Pourquoi union-first :**
- Pas de logique dupliquée pour Paris/Évry
- Cohérence garantie entre les sources
- Comparaison facile des sources via la colonne `Source`
- Passage à l'échelle vers de nouvelles villes sans modification du l'ETL

**Détails d'implémentation :**
- Ajout d'une colonne `Source` ('Paris' ou 'Evry') lors de l'union
- Utilisation de clés composites : `ID` → `ID_Source`, `ID_Adr` → `ID_Adr_Source`
- Filtrage par `Source` uniquement à l'étape finale pour les tables cibles séparées

---

![Diagramme de Mapping](../assets/images/mapping_data_quality_project.png)

### Résumé des Flux

**Chemin 1 : Consommation_CSP**
```
Population (S1+S2) → Join CSP → Enrichissement avec Salaire_Moyen
   ↓
Consommation (S1+S2) → Création adresse complète
   ↓
Join sur Adresse → Group by CSP → AVG(consommation), MAX(salaire)
```

**Chemin 2 : Consommation_IRIS (Paris/Évry)**
```
Consommation (S1+S2) → Création adresse complète
   ↓
Join IRIS (ID_Rue==Nom_Rue, ID_Ville==Code_Postal)
   ↓
Group by ID_IRIS → SUM(consommation)
   ↓
Split par Source → Cible Paris, Cible Évry
```

---

## 2. Implémentation des mappings

### Copie d'écran de l'implémentation du job

![Implémentation de Mapping](../assets/images/implementation_mapping.png)

L’implémentation des mappings a été réalisée à l’aide de l’ETL Talend.

### Problèmes rencontrés

Lors de l’implémentation, plusieurs difficultés ont été rencontrées :

- Formatage des adresses :  
Les adresses n’étaient pas uniformes entre les différentes sources. Nous avons donc choisi de les décomposer en plusieurs champs : numéro, nom de rue, ville et code postal.  
Nous avons également supprimé les accents, converti l’ensemble en minuscules et traité les cas particuliers où certaines adresses étaient manquantes.  
De plus, certains numéros de rue contenaient des lettres ou des suffixes tels que A, B, C, BIS ou TER, ce qui a nécessité un traitement spécifique.

- Codes postaux :  
Le format des codes postaux n’était pas toujours conforme : certains contenaient un caractère en trop ou n’étaient pas composés de cinq chiffres.

- CSP (Catégorie Socio-Professionnelle) :  
Nous avons dû gérer deux cas distincts selon les sources :
  - l’une faisait référence à l’identifiant du CSP,
  - l’autre à la description (le nom) du CSP.  
Il a donc fallu établir une correspondance entre ces deux formats à l’aide de la table de référence CSP.

- Échelles de consommation :  
Les valeurs de consommation n’étaient pas exprimées dans la même unité : certaines en Watt (W), d’autres en Kilowatt (kW). Une mise à l’échelle a donc été effectuée pour harmoniser les données.

- Normalisation des chaînes de caractères :  
Avant d’effectuer les jointures, toutes les chaînes ont été converties en minuscules et les accents supprimés afin d’éviter les divergences lors des comparaisons.

- Problèmes de jointure sur les noms de rue :  
Les formats différaient selon les sources : certaines ne contenaient que le nom de la rue, tandis que d’autres incluaient le type de voie (rue, boulevard, allée, etc.). Ce décalage a nécessité un nettoyage et une harmonisation supplémentaires avant la jointure.


## 3. Règles de Transformation

### Séparation des composants d’adresse

Pour harmoniser les données, les adresses ont été nettoyées puis décomposées en quatre éléments : numéro, nom de rue, ville et code postal.

1. Nettoyage  
Avant l’extraction, les adresses ont été normalisées :
- suppression des accents, guillemets et espaces inutiles,
- uniformisation des majuscules/minuscules,
- correction des séparateurs (espaces, virgules).

2. Extraction  
À l’aide d’expressions régulières :
- le code postal est identifié comme une suite de cinq chiffres ;
- le numéro de voie correspond à une suite de 1 à 4 chiffres, éventuellement suivie de bis, ter ou d’une lettre ;
- la ville est extraite selon sa position relative au code postal ou déduite de celui-ci (ex. 75 → Paris, 69 → Lyon) ;
- le nom de rue est obtenu après suppression des autres éléments, puis les abréviations de type de voie (av, bd, r, pl, etc.) sont remplacées par leur forme complète.

3. Gestion des cas particuliers  
Des règles de substitution complètent les valeurs manquantes (ex. déduction du code postal à partir de la ville) et garantissent une structure d’adresse uniforme.

### Stratégie de Jointure
Toutes les jointures sont **INNER** (abandon des enregistrements non correspondants) :
- Population ⋈ CSP : Suppression des codes CSP invalides
- Population ⋈ Consommation : Suppression des adresses non correspondantes
- Consommation ⋈ IRIS : Suppression des adresses hors zones IRIS

---

## 4. Plan d’Évaluation de la Qualité des Données

### Dimensions de Qualité Considérées

Les contrôles de qualité portent sur **4 dimensions principales** issues des besoins métiers et techniques du projet :

| Dimension | Nombre de Métriques | Préfixe ID | Priorité |
|------------|----------------------|-------------|-----------|
| Complétude | 12 | C001–C012 | Obligatoire |
| Cohérence Syntaxique | 8 | CS001–CS008 | Obligatoire |
| Granularité | 1 | G001 | Obligatoire |
| Doublons | 1 | D001 | Souhaitable |

### Complétude (C001-C012)

**Exemple: C006 - conso_kwh_non_null**

Cette métrique vérifie le taux de présence des valeurs de consommation électrique dans la table Consommation. Elle calcule le pourcentage de lignes où NB_KW_Jour n'est pas null.

*Cas d'usage:* Si cette métrique tombe à 45%, cela signifie que 55% des enregistrements n'ont pas de valeur de consommation. Le problème peut venir d'une défaillance du système de comptage ou d'un bug dans l'extraction des données depuis la source. Cette métrique permet d'alerter rapidement l'équipe data pour corriger le pipeline avant que les tables cibles ne soient impactées.

### Cohérence Syntaxique (CS001-CS008)

**Exemple: CS003 - cp_geo_valide_paris**

Cette métrique vérifie que les codes postaux de la table Consommation appartiennent bien à la plage Paris (75001-75020). Elle retourne le pourcentage de codes postaux valides pour Paris.

*Cas d'usage:* Si cette métrique descend à 60%, cela indique qu'environ 40% des codes postaux sont hors plage parisienne. Cela peut révéler une contamination des données par d'autres sources géographiques ou une erreur de mapping lors de l'intégration. Cette détection permet d'éviter des jointures incorrectes avec la table IRIS de référence.

### Granularité (G001)

**Exemple: G001 - echelle_kwh_s1_s2**

Cette métrique compare l'échelle des consommations moyennes entre deux tables sources Consommation1 et Consommation2. Elle vérifie que le ratio des moyennes est entre 0.1 et 10, retournant TRUE ou FALSE.

*Cas d'usage:* Si le ratio sort de cette plage (par exemple 1000), cela signifie qu'une des sources utilise probablement des kWh alors que l'autre utilise des Wh ou MWh. Cette détection précoce évite d'agréger des données à des échelles incompatibles dans les tables cibles, ce qui fausserait complètement les analyses de consommation par IRIS ou CSP.

### Doublons (D001)

**Exemple: D001 - conso_uni_adresse**

Cette métrique détecte les adresses dupliquées dans la table Consommation en calculant le pourcentage de doublons sur la combinaison (N, Nom_Rue, Code_Postal).

*Cas d'usage:* Si cette métrique indique 15%, cela signifie que 15% des enregistrements ont la même adresse qu'un autre enregistrement. Cela peut être légitime (plusieurs compteurs à la même adresse) ou problématique (réingestion accidentelle des mêmes données). Cette métrique permet d'investiguer et de décider si un dédoublonnage est nécessaire avant l'agrégation par IRIS.

### List des metriques

---

| ID_Métrique | Nom_Métrique | Dimension | Type_Objet | Tableau | Colonne | Phase_Données | Description_Implémentation |
|------------|--------------|-----------|------------|---------|---------|---------------|----------------------------|
| C001 | pop_adresse_non_null | Complétude | Colonne | Population | Adresse | Source | COUNT(Adresse IS NOT NULL) / COUNT(*) * 100 |
| C002 | pop_csp_non_null | Complétude | Colonne | Population | CSP | Source | COUNT(CSP IS NOT NULL) / COUNT(*) * 100 |
| C003 | conso_num_rue_non_null | Complétude | Colonne | Consommation | N | Source | COUNT(N IS NOT NULL) / COUNT(*) * 100 |
| C004 | conso_nom_rue_non_null | Complétude | Colonne | Consommation | Nom_Rue | Source | COUNT(Nom_Rue IS NOT NULL) / COUNT(*) * 100 |
| C005 | conso_cp_non_null | Complétude | Colonne | Consommation | Code_Postal | Source | COUNT(Code_Postal IS NOT NULL) / COUNT(*) * 100 |
| C006 | conso_kwh_non_null | Complétude | Colonne | Consommation | NB_KW_Jour | Source | COUNT(NB_KW_Jour IS NOT NULL) / COUNT(*) * 100 |
| C007 | csp_ref_id | Complétude | Table | CSP | ID_CSP | Source | COUNT(*) WHERE any column IS NOT NULL / COUNT(*) * 100 |
| C008 | csp_ref_salaire_moyen | Complétude | Column | CSP | Salaire_Moyen | Source | COUNT(*) WHERE Salaire_Moyen IS NOT NULL / COUNT(*) * 100 |
| C009 | csp_ref_desc | Complétude | Column | CSP | Desc | Source | COUNT(*) WHERE Desc IS NOT NULL / COUNT(*) * 100 |
| C010 | iris_ref_id_rue | Complétude | Column | IRIS | ID_Rue | Source | COUNT(*) WHERE ID_Rue IS NOT NULL / COUNT(*) * 100 |
| C011 | iris_ref_id_ville | Complétude | Column | IRIS | ID_Ville | Source | COUNT(*) WHERE ID_Ville IS NOT NULL / COUNT(*) * 100 |
| C012 | id_ref_ris | Complétude | Column | IRIS | ID_Iris | Source | COUNT(*) WHERE ID_Iris IS NOT NULL / COUNT(*) * 100 |
| C013 | target_iris_complet | Complétude | Table | Consommation_IRIS | ID_IRIS\|Conso_moyenne_annuelle | Cible | COUNT(*) WHERE any column IS NOT NULL / COUNT(*) * 100 |
| C014 | target_csp_complet | Complétude | Table | Consommation_CSP | ID_CSP\|Conso_moyenne_annuelle\|Salaire_Moyen | Cible | COUNT(*) WHERE any column IS NOT NULL / COUNT(*) * 100 |
| CS001 | conso_num_rue_positif | Cohérence Syntaxique | Colonne | Consommation | N | Source | COUNT(WHERE N IS INTEGER AND N > 0) / COUNT(*) * 100 |
| CS002 | conso_kwh_positif | Cohérence Syntaxique | Colonne | Consommation | NB_KW_Jour | Source | COUNT(WHERE NB_KW_Jour >= 0) / COUNT(*) * 100 |
| CS003 | cp_geo_valide_paris | Cohérence Syntaxique | Colonne | Consommation | Code_Postal | Source | COUNT(WHERE Code_Postal BETWEEN 75001 AND 75020) / COUNT(*) * 100 |
| CS004 | cp_geo_valide_evry | Cohérence Syntaxique | Colonne | Consommation | Code_Postal | Source | COUNT(Code_Postal BETWEEN 91000 AND 91099) / COUNT(*) * 100 |
| CS005 | iris_rue_normalisee | Cohérence Syntaxique | Colonne | IRIS | ID_Rue | Source | COUNT(WHERE Minuscules + trimmed pour correspondance) / COUNT(*) * 100 |
| CS006 | pop_csp_domaine1 | Cohérence Syntaxique | Colonne | Population1 | CSP | Source | COUNT(WHERE CSP IN (CSP.desc)) / COUNT(*) * 100 |
| CS007 | pop_csp_domaine2 | Cohérence Syntaxique | Colonne | Population2 | CSP | Source | COUNT(WHERE CSP IN (1,2,3,4,5,6) / COUNT(*) * 100 |
| CS008 | adresse_format_standard_paris | Cohérence Syntaxique | Colonne | Population1 | Adresse | Source | COUNT(WHERE "Format correspond à 'Ville, N Nom_Rue'") / COUNT(*) * 100 |
| CS009 | adresse_format_standard_evry | Cohérence Syntaxique | Colonne | Population2 | Adresse | Source | COUNT(WHERE "Format correspond à 'Ville,Code_postal, N Nom_Rue'") / COUNT(*) * 100 |
| G001 | echelle_kwh_s1_s2 | Granularité | Colonne | Consommation1, Consommation 2 | NB_KW_Jour | Source | MEAN(S1.NB_KW_Jour) / MEAN(S2.NB_KW_Jour) IS BETWEEN 0.1 AND 10.0 (OUTPUT => TRUE OR FALSE) |
| D001 | conso_uni_adresse | Doublons | Colonne | Consommation | Adresse | Inter | (COUNT(N, Nom_Rue, Code_Postal) - COUNT(DISTINCT (N, Nom_Rue, Code_Postal))) / COUNT(*) * 100 |

---

### Justification de la Granularité des Métriques

Les métriques de qualité sont volontairement granulaires, c'est-à-dire définies au niveau colonne plutôt qu'au niveau table global. Cette approche permet d'identifier précisément la source des problèmes de qualité et d'accélérer leur résolution.
Exemple concret avec la complétude:
Au lieu d'une seule métrique globale pour la table Consommation, on a défini 4 métriques séparées:

- C003: conso_num_rue_non_null (colonne N)
- C004: conso_nom_rue_non_null (colonne Nom_Rue)
- C005: conso_cp_non_null (colonne Code_Postal)
- C006: conso_kwh_non_null (colonne NB_KW_Jour)

Si on avait une métrique globale indiquant "Consommation: 75% de complétude", on saurait qu'il y a un problème mais pas où. Avec les métriques granulaires, on obtient par exemple:

- C003 (N): 98%
- C004 (Nom_Rue): 95%
- C005 (Code_Postal): 92%
- C006 (NB_KW_Jour): 45%

Le problème est immédiatement localisé sur NB_KW_Jour. On peut alors investiguer directement la source de cette colonne sans perdre de temps à analyser les autres.
Bénéfices opérationnels:

1. Diagnostic rapide: Identification immédiate de la colonne problématique
   
2. Priorisation: Les colonnes critiques (comme Code_Postal pour les jointures avec IRIS) peuvent avoir des seuils d'alerte plus stricts que les colonnes optionnelles
3. Traçabilité: Quand une ingestion échoue partiellement, on voit exactement quelle partie du processus ETL est impactée
4. Monitoring ciblé: Suivi de l'évolution de chaque colonne dans le temps pour détecter les dégradations progressives

Cette logique s'applique aussi aux autres dimensions. Pour la cohérence syntaxique, on a par exemple CS003 et CS004 qui vérifient les codes postaux Paris et Evry séparément au lieu d'une validation générique, permettant d'identifier si le problème vient d'une source géographique spécifique.

---

## 5. Résultats des Métriques de Qualité

### Vue d'ensemble

| Dimension | Total Métriques | Résultat Global |
|-----------|-----------------|-----------------|
| Complétude | 12 | Acceptable (83-100%) |
| Cohérence Syntaxique | 8 | Problématique (25-100%) |
| Granularité | 1 | Échec (FALSE) |
| Doublons | 1 | OK (0%) |

### Complétude - Qualité Acceptable

Les données sources sont globalement complètes avec 10 métriques au-dessus de 90%. Deux points d'attention:

- **C007 et C008 (83,33%)**: Tables CSP de référence incomplètes sur ID_CSP et Salaire_Moyen. Environ 17% des lignes manquent ces informations, ce qui peut limiter les jointures et analyses par catégorie socioprofessionnelle.
- **C006 (80%)**: 20% des enregistrements Consommation n'ont pas de valeur NB_KW_Jour. Problème modéré mais acceptable si ces lignes correspondent à des compteurs inactifs.

Les colonnes critiques pour les jointures (Code_Postal, adresses, identifiants IRIS) sont toutes à 100%.

### Cohérence Syntaxique - Problèmes Majeurs Détectés

**Codes postaux hors normes:**
- **CS003 (48%)**: Seulement 48% des codes postaux sont dans la plage Paris (75001-75020)
- **CS004 (36%)**: Seulement 36% sont dans la plage Evry (91000-91099)

Ces résultats indiquent une contamination importante des données par d'autres zones géographiques ou des erreurs de saisie. Plus de la moitié des données ne correspondent pas aux périmètres géographiques attendus. Impact direct sur la fiabilité des agrégations par IRIS.

**CSP non conformes:**
- **CS005 (25%)**: Seulement 25% des CSP de Population_Paris correspondent aux valeurs de la table de référence

75% des catégories socioprofessionnelles ne matchent pas avec le référentiel. Cela rend impossible une jointure fiable entre Population et CSP de référence pour récupérer les salaires moyens.

**Formats d'adresse:**
- **CS008 (58,33%)**: Format Evry non standard sur 42% des adresses

**Validations positives:**
- CS002 (80%): Consommations positives correctes
- CS006 (100%): CSP Population_Evry conformes au domaine numérique
- CS007 (100%): Format Paris respecté

### Granularité - Échec Critique

**G001 (FALSE)**: Le ratio des consommations moyennes entre Consommation_Paris et Consommation_Evry est hors de la plage [0.1, 10].

Les deux sources utilisent des unités ou échelles différentes (probablement Wh vs kWh ou kWh vs MWh). Les données ne peuvent pas être agrégées directement sans transformation. Il faut identifier quelle source utilise quelle unité et appliquer un facteur de conversion avant toute consolidation.

### Doublons - Aucun Problème

**D001 (0%)**: Aucun doublon détecté sur les adresses dans Consommation.

Chaque combinaison (N, Nom_Rue, Code_Postal) est unique. Les données sont propres de ce point de vue.

### Recommandations Prioritaires

1. **Urgent**: Corriger le problème d'échelle des consommations (G001) avant toute agrégation
2. **Important**: Investiguer la source des codes postaux hors périmètre (CS003, CS004) - possible mélange de datasets
3. **Important**: Vérifier le mapping CSP entre Population1 et la table de référence (CS005)
4. **Souhaitable**: Compléter les tables de référence CSP (C007, C008)

---

## 6. Amélioration

### Amélioration de la complétude

La complétude des données concerne les valeurs manquantes (null). Malheureusement, il n’est pas possible d’améliorer cette dimension sans disposer de sources externes ou de règles de déduction fiables. En d’autres termes, on ne peut pas créer ou deviner des valeurs à partir de données inexistantes.

### Amélioration de la cohérence syntaxique

Concernant la cohérence syntaxique, certaines anomalies ont été observées dans les tables de consommation, notamment au niveau des codes postaux (erreurs de saisie, caractères parasites, zéros en trop, etc.).
Pour corriger ces problèmes, on peut appliquer un nettoyage automatique à l’aide d’expressions régulières : elles permettraient de repérer les schémas de type 75--- ou 91--- et de supprimer les caractères indésirables ou les zéros surnuméraires, qu’ils se trouvent en début, au milieu ou à la fin de la chaîne.

Dans la table Population_Paris, les valeurs de la variable CSP ne correspondent pas toujours aux intitulés de la table de référence CSP. Ces incohérences peuvent provenir de variations de genre (masculin/féminin), de nombre (singulier/pluriel) ou de fautes de frappe.
Pour corriger cela, nous avons mis en place une détection par racine de mots : par exemple, si une valeur contient les chaînes commerç ou arstisan, elle sera associée à la catégorie « Artisans, commerçants et chefs d’entreprise » de la table CSP.

### Amélioration de la granularité

Après analyse, nous avons constaté un facteur d’échelle de 1 000 entre deux sources : l’une exprimait les valeurs en W/h, l’autre en kW/h.
Pour harmoniser la granularité, une simple division par 1 000 des valeurs exprimées en W/h permet d’obtenir une cohérence entre les deux tables Consommation.
