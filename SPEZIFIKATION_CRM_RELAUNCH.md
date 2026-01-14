# Spezifikation: CRM/Intranet Relaunch

**Projekt:** Atikon CRM/Intranet System Relaunch
**Erstellt:** 09.01.2026
**Basierend auf:** Video-Analyse der bestehenden Arbeitsabläufe
**Status:** Entwurf - zur Ergänzung durch weitere Abläufe

---

## 1. Executive Summary

### 1.1 Überblick

Das bestehende System besteht aus mehreren Komponenten:
- **Atikon Intranet/CRM**: Webbasierte Anwendung für Lead-/Kundenverwaltung, Aufgabenmanagement und Kommunikation
- **Meta Ads Manager**: Externe Plattform für Werbekampagnen-Management (Facebook/Instagram)
- **Landing Pages**: Lead-Generierung über dedizierte Webseiten (atikon.com)
- **Excel-Tracking**: Manuelles Lead-Tracking als Zwischenlösung

### 1.2 Kernfunktionalität

| Bereich | Beschreibung |
|---------|--------------|
| **Lead-Generierung** | Social Media Ads → Landing Page → Formular → Lead-Erfassung |
| **Lead-Verarbeitung** | Excel-Import → CRM-Suche → Kontaktverlauf → Aufgabenzuweisung |
| **Kundenmanagement** | Stammdatenpflege, Potenzialanalyse, Kontakthistorie |
| **Aufgabenverwaltung** | Erstellung, Zuweisung, Nachverfolgung, Folgeaufgaben |
| **Kommunikation** | E-Mail-Versand (Vorlagen), Outlook-Kalenderintegration |

### 1.3 Zielgruppen

- **Marketing-Manager**: Kampagnenmanagement, Lead-Generierung
- **Callcenter-/Vertriebsmitarbeiter**: Lead-Qualifizierung, Erstansprache
- **Telefonmarketing-Team**: Lead-Nachverfolgung, Terminvereinbarung
- **Externe Leads**: Potenzielle Kunden (Steuerberater)

---

## 2. Workflow-Dokumentation

### 2.1 End-to-End Lead-Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LEAD-GENERIERUNG (Marketing)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Meta Ads Manager                                                         │
│     └── Kampagne erstellen (Budget, Zielgruppe, Anzeigen)                   │
│  2. Facebook/Instagram                                                       │
│     └── Werbeanzeige mit "Herunterladen"-Button                             │
│  3. Landing Page (atikon.com)                                               │
│     └── Lead-Formular: Vorname, Nachname, E-Mail, Telefon, Firma            │
│  4. Danke-Seite + E-Mail mit Playbook                                       │
│  5. Lead-Daten → Excel-Tracking-Sheet                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LEAD-VERARBEITUNG (Callcenter)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. Excel-Liste prüfen (täglich)                                            │
│     └── Lead identifizieren, Daten kopieren                                 │
│  7. Intranet-Suche                                                          │
│     └── Kontakt im CRM suchen/anlegen                                       │
│  8. Callcenter-Ansicht                                                      │
│     └── Kontaktdetails, Verlauf, Aufgaben anzeigen                          │
│  9. Notiz hinzufügen                                                        │
│     └── Lead-Informationen dokumentieren                                    │
│ 10. Aufgabe erstellen                                                       │
│     └── "Nachfassen" an Telefonmarketing zuweisen                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LEAD-QUALIFIZIERUNG (Telefonmarketing)                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 11. Aufgabenliste prüfen (MyTasks)                                          │
│     └── Zugewiesene Aufgaben bearbeiten                                     │
│ 12. Potenzialanalyse                                                        │
│     └── Website prüfen → Mitarbeiteranzahl → Potenzial (A/B/C/D)            │
│ 13. Kundendaten pflegen                                                     │
│     └── Potenzial, VPM, Branche aktualisieren                               │
│ 14. Kontaktdaten pflegen                                                    │
│     └── Leadstatus ("Warm"), Newsletter-Opt-in                              │
│ 15. Telefonische Kontaktaufnahme                                            │
│     └── Qualifizierung, Terminvereinbarung                                  │
│ 16. Terminbestätigung                                                       │
│     └── E-Mail-Vorlage senden + Outlook-Termin                              │
│ 17. Aufgabe abschließen + Folgeaufgabe                                      │
│     └── Status "Erledigt/Verschoben", Terminerinnerung anlegen              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Zeitstempel-Referenz

| Video | Zeitstempel | Aktion |
|-------|-------------|--------|
| Video 2 | 00:00-01:00 | Meta Ads Manager - Kampagnenübersicht & Ad-Bearbeitung |
| Video 2 | 01:08-01:23 | Facebook-Feed mit Werbeanzeige |
| Video 2 | 01:27-01:55 | Landing Page - Formular ausfüllen |
| Video 2 | 01:55-02:00 | Danke-Seite |
| Video 2 | 02:20-03:17 | Excel-Tracking - Lead-Verwaltung |
| Video 1 | 00:00-00:12 | Excel-Liste - Lead identifizieren |
| Video 1 | 00:15-00:22 | Intranet-Suche - Kontakt finden |
| Video 1 | 00:23-00:48 | Callcenter-Ansicht - Details anzeigen |
| Video 1 | 00:49-01:13 | Notiz hinzufügen |
| Video 1 | 01:17-02:07 | Aufgabe erstellen & zuweisen |
| Video 1 | 02:29-02:33 | Aufgabenliste (MyTasks) |
| Video 1 | 02:37-02:50 | Potenzialanalyse (Website) |
| Video 1 | 02:59-03:24 | Kundendaten pflegen |
| Video 1 | 03:25-03:40 | Kontaktdaten pflegen |
| Video 1 | 03:51-04:02 | E-Mail-Terminbestätigung |
| Video 1 | 04:05-04:15 | Outlook-Termineinladung (verbal) |
| Video 1 | 04:39-04:57 | Aufgabe abschließen & Folgeaufgabe |

---

## 3. Benutzeroberfläche (UI)

### 3.1 Intranet/CRM - Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER                                                               │
│ [Logo: atikon Intranet]  [Tabs: Allgemein | Vertrieb | KUND | ...]  │
│                          [Suchfeld mit Autovervollständigung]  [👤] │
├────────────────┬────────────────────────────────────────────────────┤
│ SIDEBAR        │ CONTENT-BEREICH                                    │
│                │                                                     │
│ Anzeigeoptionen│ ┌─────────────────────────────────────────────────┐│
│ ☑ Kontaktverlauf│ │ CALLCENTER-ANSICHT                              ││
│ ☑ Produkte     │ │                                                  ││
│ ☑ Produkthistorie│ │ [Details-Panel] [Kontaktverlauf] [Aufgaben]    ││
│ ☑ Rechnungen   │ │                                                  ││
│ ☐ Aktuelle...  │ │ Name: Mag. Alexander Gutmann                     ││
│                │ │ Firma: Gutmann Consulting Steuerberatung         ││
│ ─────────────  │ │ Leadstatus: Warm                                 ││
│ Aktionen       │ │ Potenzial: B                                     ││
│ [E-Mail senden]│ │                                                  ││
│ [Dokument...]  │ │ Kontaktverlauf:                                  ││
│ [Film]         │ │ • 09.01.2026 - Anfrage ChatGPT Playbook          ││
│                │ │ • 08.01.2026 - Newsletter angemeldet             ││
│                │ └─────────────────────────────────────────────────┘│
└────────────────┴────────────────────────────────────────────────────┘
```

### 3.2 Hauptansichten

| Ansicht | Beschreibung | Zugangspunkt |
|---------|--------------|--------------|
| **Callcenter-Ansicht** | Zentrale Kontaktansicht mit Details, Verlauf, Aufgaben | Suche → Kontakt auswählen |
| **Aufgabenliste (MyTasks)** | Alle zugewiesenen Aufgaben tabellarisch | Vertrieb → Aufgaben |
| **Kundendaten** | Stammdaten des Unternehmens | Kontakt → Kundendaten-Tab |
| **Kontaktbearbeitung** | Persönliche Daten eines Ansprechpartners | Kundendaten → Kontakt bearbeiten |

### 3.3 UI-Komponenten

#### Modale Dialoge

| Dialog | Felder | Aktionen |
|--------|--------|----------|
| **Notiz hinzufügen** | Textarea (Notizinhalt) | Speichern |
| **Aufgabe erstellen** | Datum, Zeit, Mitarbeiter, Priorität (1-5), Benachrichtigung (Checkbox), Notizen | Erstellen |
| **Aufgabe bearbeiten** | Notizen, Status-Dropdown, Folgeaufgabe-Checkbox + Felder | Speichern |
| **E-Mail senden** | Vorlage-Dropdown, Betreff, Vorschau, Anhänge | Versenden |
| **Kontakt bearbeiten** | Anrede, Titel, Name, Zuständigkeit, Leadstatus, Newsletter, Telefon, E-Mail | Speichern |

### 3.4 Landing Page - Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: [Logo: Atikon - Alles Marketing]                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Nutzen Sie ChatGPT so, wie es nur                                 │
│   die Top-1 % der Kanzleien tun.                                    │
│                                                                      │
│   [────────────────────────────────]                                │
│   [  jetzt kostenlos anfordern  ▼ ]                                 │
│   [────────────────────────────────]                                │
│                                              [Playbook-Grafik]      │
├─────────────────────────────────────────────────────────────────────┤
│ LEAD-FORMULAR                                                        │
│                                                                      │
│ Vorname*:    [________________________]                             │
│ Nachname*:   [________________________]                             │
│ E-Mail*:     [________________________]                             │
│ Telefon*:    [________________________]                             │
│ Firma*:      [________________________]                             │
│                                                                      │
│ ☑ Datenschutzbestimmungen gelesen und akzeptiert                    │
│                                                                      │
│ [─────────────────────────────────────]                             │
│ [    jetzt kostenfrei anfordern      ]                              │
│ [─────────────────────────────────────]                             │
├─────────────────────────────────────────────────────────────────────┤
│ FOOTER: Über uns | Online Marketing | Grafikdesign | ...            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Datenmodell

### 4.1 Entitäten-Übersicht

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    Kampagne      │     │     Firma        │     │    Mitarbeiter   │
│    (Campaign)    │     │   (Customer)     │     │    (Employee)    │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ - ID             │     │ - ID             │     │ - ID             │
│ - Name           │     │ - Firma*         │     │ - Kennung (MLIN) │
│ - Status         │     │ - Branche        │     │ - Name           │
│ - Budget         │     │ - Land           │     │ - Rolle          │
│ - Ergebnisse     │     │ - Website        │     └────────┬─────────┘
│ - Kosten         │     │ - Adresse        │              │
└────────┬─────────┘     │ - Telefon        │              │
         │               │ - E-Mail         │              │
         │               │ - Mitarbeiteranzahl│            │
         │               │ - Potenzial (A-D)│              │
         │               │ - Zuständiger VPM│──────────────┘
         │               └────────┬─────────┘
         │                        │ 1:N
         │                        ↓
         │               ┌──────────────────┐     ┌──────────────────┐
         │               │     Kontakt      │────→│   Aufgabe        │
         │               │    (Contact)     │ 1:N │    (Task)        │
         │               ├──────────────────┤     ├──────────────────┤
         │               │ - ID             │     │ - ID             │
         │               │ - Anrede         │     │ - Datum/Zeit     │
         │               │ - Titel          │     │ - Mitarbeiter    │
         │               │ - Vorname        │     │ - Priorität (1-5)│
         │               │ - Nachname       │     │ - Status         │
         │               │ - Zuständigkeit  │     │ - Notizen        │
         │               │ - Leadstatus     │     └──────────────────┘
         │               │ - Newsletter     │
         │               │ - Telefon/Mobil  │     ┌──────────────────┐
         │               │ - E-Mail         │────→│ Kontaktverlauf   │
         │               └──────────────────┘ 1:N │ (ContactHistory) │
         │                                        ├──────────────────┤
         │                                        │ - ID             │
         │                                        │ - Zeitstempel    │
         ↓                                        │ - Mitarbeiter    │
┌──────────────────┐                              │ - Notizinhalt    │
│      Lead        │                              └──────────────────┘
│  (Excel/Import)  │
├──────────────────┤
│ - Kampagne       │
│ - Vorname        │
│ - Nachname       │
│ - Firma          │
│ - E-Mail         │
│ - Telefon        │
│ - Domain         │
│ - Datum          │
│ - Bearbeiter     │
│ - Lead-Status    │
└──────────────────┘
```

### 4.2 Entitäten-Details

#### Lead (Import aus Excel)
| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| Kampagne | String | Name der Marketing-Kampagne |
| Vorname | String | * Pflichtfeld |
| Nachname | String | * Pflichtfeld |
| Firma | String | Firmenname |
| E-Mail | String | * Pflichtfeld, E-Mail-Format |
| Telefon | String | Telefonnummer |
| Domain | String | Extrahiert aus E-Mail/Website |
| Datum | Date | Datum der Anfrage |
| Bearbeiter | String | Zugewiesener Mitarbeiter |
| Lead-Status | Enum | Neu, Kontaktiert, Qualifiziert, Nicht qualifiziert |

#### Firma (Customer)
| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| Firma | String | * Pflichtfeld |
| Branche | Dropdown | z.B. "Steuerberater" |
| Land | Dropdown | z.B. "Österreich" |
| Website | URL | Firmenwebsite |
| Adresse | Object | Straße, PLZ, Ort, Bundesland |
| Telefon | String | Haupt-Telefonnummer |
| E-Mail | String | Haupt-E-Mail |
| Mitarbeiteranzahl | Integer | Für Potenzialberechnung |
| Standortanzahl | Integer | |
| Potenzial | Enum | A (>20 MA), B (10-20), C (<10), D (Einzelkämpfer) |
| Zuständiger VPM | FK | Vertriebspartner-Manager |
| Zuständiger MA | FK | Betreuender Mitarbeiter |
| Buyer Persona | Dropdown | Kundentyp |

#### Kontakt (Contact)
| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| Hauptkontakt | Boolean | Primärer Ansprechpartner |
| Anrede | Dropdown | Herr, Frau |
| Redestatus | Dropdown | "Sehr geehrter Herr" |
| Titel | String | Mag., Dr., etc. |
| Vorname | String | |
| Nachname | String | |
| Zuständigkeit | Dropdown | * Geschäftsführung, etc. |
| Leadstatus | Dropdown | Warm, Kalt, Open |
| Personenzahl | Dropdown | |
| Newsletter | Boolean | Opt-in |
| Aussendung | Boolean | Marketing-Mails |
| Telefon | String | Festnetz |
| Mobil | String | Mobilnummer |
| Fax | String | |
| E-Mail | String | |

#### Aufgabe (Task)
| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| Datum | Date | Fälligkeitsdatum |
| Zeit | Time | Fälligkeitszeit |
| Mitarbeiter | FK | Zugewiesen an |
| Priorität | Integer | 1-5 (1 = Standard) |
| Keine Benachrichtigung | Boolean | |
| Notizen | Text | Beschreibung der Aufgabe |
| Status | Enum | Offen, Verschoben, Erledigt |
| Kontakt | FK | Verknüpfter Kontakt |

#### Kontaktverlauf (ContactHistory)
| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| Zeitstempel | DateTime | Automatisch |
| Mitarbeiter | FK | Ersteller |
| Notizinhalt | Text | Freitext |
| Kontakt | FK | Verknüpfter Kontakt |

---

## 5. Funktionale Anforderungen

### 5.1 Must-Have (Kernfunktionen)

| ID | Funktion | Beschreibung | Priorität |
|----|----------|--------------|-----------|
| F01 | **Lead-Import** | Automatisierter Import aus Excel/CSV oder direkter Landing-Page-Integration | Hoch |
| F02 | **Kontaktsuche** | Schnelle Suche mit Autovervollständigung nach Name, Firma, E-Mail | Hoch |
| F03 | **Callcenter-Ansicht** | Zentrale Übersicht: Details, Kontaktverlauf, Aufgaben | Hoch |
| F04 | **Kontaktverlauf** | Chronologische Dokumentation aller Interaktionen | Hoch |
| F05 | **Aufgabenverwaltung** | Erstellen, Zuweisen, Statusänderung, Folgeaufgaben | Hoch |
| F06 | **Stammdatenpflege** | Bearbeitung von Firmen- und Kontaktdaten | Hoch |
| F07 | **E-Mail-Vorlagen** | Versand vorkonfigurierter E-Mails (Terminbestätigung, etc.) | Hoch |
| F08 | **Lead-Übersicht** | Tabellarische Ansicht aller Leads mit Filter/Sortierung | Hoch |
| F09 | **Landing Page** | Lead-Formular mit automatischer Datenerfassung | Hoch |
| F10 | **Auto-E-Mail** | Automatischer Versand von Lead-Magnets nach Formular-Submit | Hoch |

### 5.2 Should-Have (Wichtige Features)

| ID | Funktion | Beschreibung | Priorität |
|----|----------|--------------|-----------|
| F11 | **Potenzialanalyse** | Automatische Ermittlung des Potenzials basierend auf Mitarbeiteranzahl | Mittel |
| F12 | **Kalenderintegration** | Outlook/Google Calendar Termineinladungen | Mittel |
| F13 | **RBAC** | Rollenbasierte Zugriffskontrolle | Mittel |
| F14 | **Audit-Logs** | Protokollierung aller Änderungen | Mittel |
| F15 | **Dashboard** | KPIs: Leads/Kampagne, Status-Verteilung, Conversion | Mittel |
| F16 | **Export** | CSV/Excel-Export von Lead-Daten | Mittel |
| F17 | **Meta Ads Integration** | Automatische Übernahme von Kampagnen-Metadaten | Mittel |

### 5.3 Nice-to-Have (Optionale Features)

| ID | Funktion | Beschreibung | Priorität |
|----|----------|--------------|-----------|
| F18 | **Lead-Scoring** | Automatische Bewertung von Leads | Niedrig |
| F19 | **A/B-Testing** | Landing Page Varianten testen | Niedrig |
| F20 | **E-Mail-Sequenzen** | Automatisierte Follow-up E-Mails | Niedrig |
| F21 | **CRM-Integration** | Anbindung an Salesforce/HubSpot | Niedrig |
| F22 | **Mobile App** | Native App für Vertrieb unterwegs | Niedrig |
| F23 | **KI-Vorschläge** | Automatische Empfehlungen für nächste Aktionen | Niedrig |

---

## 6. Benutzerrollen & Berechtigungen

### 6.1 Rollenmatrix

| Funktion | Marketing-Manager | Callcenter | Telefonmarketing | Admin |
|----------|:-----------------:|:----------:|:----------------:|:-----:|
| Lead-Import | ✓ | ✓ | - | ✓ |
| Kontaktsuche | ✓ | ✓ | ✓ | ✓ |
| Kontaktdetails lesen | ✓ | ✓ | ✓ | ✓ |
| Kontaktdetails bearbeiten | - | ✓ | ✓ | ✓ |
| Aufgaben erstellen | ✓ | ✓ | ✓ | ✓ |
| Aufgaben zuweisen | - | ✓ | - | ✓ |
| Aufgaben bearbeiten | - | ✓ | ✓ (eigene) | ✓ |
| E-Mail senden | ✓ | ✓ | ✓ | ✓ |
| Kundendaten bearbeiten | - | ✓ | ✓ | ✓ |
| Landing Pages verwalten | ✓ | - | - | ✓ |
| Kampagnen verwalten | ✓ | - | - | ✓ |
| Reporting | ✓ | - | - | ✓ |
| Benutzerverwaltung | - | - | - | ✓ |

### 6.2 Sichtbare Mitarbeiter im Video

| Kennung | Name | Rolle |
|---------|------|-------|
| MLIN | Manuel Leiner | Callcenter-Mitarbeiter |
| CKN | Christina Knoegler | Telefonmarketing |

---

## 7. Technische Empfehlungen

### 7.1 Vorgeschlagener Technologie-Stack

| Komponente | Empfehlung | Alternative |
|------------|------------|-------------|
| **Frontend** | React.js + TypeScript | Vue.js, Angular |
| **UI-Bibliothek** | Tailwind CSS + Headless UI | MUI, Chakra UI |
| **Backend** | Node.js + NestJS | Python + FastAPI |
| **Datenbank** | PostgreSQL | MySQL |
| **ORM** | Prisma | TypeORM |
| **Auth** | JWT + RBAC | OAuth 2.0 |
| **E-Mail** | SendGrid | Mailgun, AWS SES |
| **Kalender** | Microsoft Graph API | Google Calendar API |
| **CMS (Landing Pages)** | Next.js + Contentful | Strapi |
| **Deployment** | Docker + Kubernetes | AWS ECS |
| **Hosting** | AWS / Azure | GCP |

### 7.2 Komplexitätsschätzung

| Feature | Komplexität | Begründung |
|---------|-------------|------------|
| Lead-Import (Excel) | Mittel | Parsing, Validierung, Fehlerbehandlung |
| Kontaktsuche | Mittel | Volltextsuche, Indexierung |
| Callcenter-Ansicht | Mittel | Multiple Datenquellen, modulare Panels |
| Kontaktverlauf | Einfach | Standard CRUD |
| Aufgabenverwaltung | Mittel | Workflow-Logik, Benachrichtigungen |
| E-Mail-Vorlagen | Einfach | Template-Engine, SMTP |
| Kalenderintegration | Mittel | API-Integration, OAuth |
| RBAC | Mittel | Rollen, Policies |
| Dashboard | Mittel | Aggregation, Visualisierung |
| Meta Ads Integration | Komplex | API-Stabilität, Rate Limits |

---

## 8. Offene Fragen

### 8.1 Fachliche Fragen

- [ ] Welche genauen Leadstatus-Werte und Übergänge gibt es?
- [ ] Wie wird das Potenzial (A/B/C/D) genau berechnet? Nur Mitarbeiteranzahl?
- [ ] Welche E-Mail-Vorlagen existieren neben "Terminbestätigung"?
- [ ] Wie viele Leads werden monatlich erwartet?
- [ ] Welche weiteren Kampagnen-Typen außer "ChatGPT-Playbook" gibt es?
- [ ] Gibt es DSGVO-spezifische Anforderungen über Standard hinaus?

### 8.2 Technische Fragen

- [ ] Bestehende Datenbank-Struktur des Intranets?
- [ ] Welche APIs sind bereits vorhanden?
- [ ] Integration mit ERP/Buchhaltungssystem erforderlich?
- [ ] Single Sign-On (SSO) Anforderungen?
- [ ] Performance-SLAs (Ladezeiten, Gleichzeitige Nutzer)?

### 8.3 Prozessfragen

- [ ] Wie werden Benachrichtigungen bei neuen Aufgaben zugestellt?
- [ ] Archivierungsstrategie für alte Leads/Kontakte?
- [ ] Backup- und Recovery-Anforderungen?

---

## 9. Nächste Schritte

1. **Klärung offener Fragen** mit Stakeholdern
2. **Ergänzung weiterer Workflows** durch zusätzliche Video-Analysen
3. **Priorisierung der Features** im Backlog
4. **Technische Architektur** detaillieren
5. **UI/UX-Design** für neue Oberfläche
6. **Datenmigrationsstrategie** vom Altsystem

---

## Anhang: Video-Quellen

| Video | Datei | Beschreibung |
|-------|-------|--------------|
| Video 1 | MicrosoftTeams-video.mp4 | CRM/Intranet - Lead-Verarbeitung, Aufgabenverwaltung |
| Video 2 | MicrosoftTeams-video (1).mp4 | Marketing - Meta Ads, Landing Page, Lead-Generierung |

---

*Diese Spezifikation wird kontinuierlich erweitert, sobald weitere Arbeitsabläufe dokumentiert werden.*
