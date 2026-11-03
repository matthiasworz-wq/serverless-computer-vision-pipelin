# Konzeptblatt Phase 2
## Serverless Computer-Vision-Pipeline zur Bildqualitätsprüfung

**Projekt:** IU Cloud Programming, Aufgabe 2  
**Technologie:** AWS, Terraform, Python 3.12 und Pillow  
**Zielregion:** Stockholm (`eu-north-1`)  
**Status:** Studienprototyp; technische Dokumentation, kein vollständiger IU-Projektbericht

## 1. Geschäftsszenario

Ein kleiner Onlinehändler für gebrauchte Elektronik erhält ungefähr 100 Produktbilder pro Monat. Vor der Veröffentlichung soll automatisch geprüft werden, ob die Bilder technisch geeignet sind. Zu dunkle, kontrastarme, unscharfe oder zu kleine Bilder werden markiert und von einer Mitarbeiterin oder einem Mitarbeiter manuell geprüft.

Das Unternehmen hat ein kleines IT-Team und möchte keinen Server dauerhaft betreiben. Die Verarbeitung soll deshalb ereignisgesteuert, reproduzierbar und kostensensibel erfolgen.

## 2. Problemstellung und Ziel

Eine manuelle Qualitätsprüfung jedes Bildes kostet Zeit und führt zu uneinheitlichen Entscheidungen. Die Cloud-Lösung soll nach jedem Upload automatisch messbare Bildmerkmale berechnen und eine nachvollziehbare Ersteinschätzung speichern.

Die Anwendung soll:

- JPEG-, JPG- und PNG-Bilder automatisch verarbeiten,
- Bildformat, Abmessungen und Dateigröße erfassen,
- Helligkeit, Kontrast und Schärfe heuristisch bewerten,
- einen Qualitätswert und eine Qualitätsklasse erzeugen,
- die Ergebnisse strukturiert speichern,
- ohne dauerhaft laufende Server auskommen,
- ohne Amazon Rekognition oder andere externe Vision-APIs funktionieren,
- mit Terraform vollständig reproduzierbar bereitgestellt werden.

## 3. Abgrenzung

Die Lösung ist eine **klassische Bildverarbeitung** und keine Objekterkennung. Pillow erkennt keine Gegenstände, Gesichter oder Texte. Die Anwendung beantwortet ausschließlich die Frage:

> Ist dieses Bild aufgrund einfacher technischer Qualitätsmerkmale für eine weitere Nutzung geeignet?

Objekt- oder Texterkennung kann später als optionale Erweiterung ergänzt werden. Sie ist nicht Bestandteil der aktuellen, kostenlosen Phase-2-Umsetzung.

## 4. Architektur und Datenfluss

```text
Nutzer-Upload
     |
     v
Privater Amazon-S3-Bucket
     |
     | ObjectCreated-Ereignis
     v
AWS Lambda, Python 3.12
     |
     +-- Bild aus S3 laden
     +-- Analyse mit Pillow
     +-- Ergebnis in DynamoDB speichern
     |
     +-- Fehler nach Wiederholung an SQS-DLQ
     |
     +-- Ausführung in CloudWatch Logs
```

### Eingesetzte Dienste

| Dienst | Aufgabe |
|---|---|
| Amazon S3 | Privater Eingangsspeicher für Testbilder |
| AWS Lambda | Ereignisgesteuerte Verarbeitung ohne Serverbetrieb |
| Pillow | Lokale Bildanalyse innerhalb der Lambda-Funktion |
| Amazon DynamoDB | Speicherung der Analyseergebnisse |
| Amazon SQS | Dead-Letter-Queue für fehlgeschlagene Lambda-Aufrufe |
| Amazon CloudWatch Logs | Nachvollziehbarkeit und Fehleranalyse |
| Terraform | Infrastruktur als Code |

## 5. Bildanalyse

Lambda lädt das Bild aus S3 und prüft zunächst Format und Dateigröße. Danach wird eine verkleinerte Arbeitskopie analysiert, damit der Speicher- und Rechenaufwand begrenzt bleibt.

Berechnete Merkmale:

- **Format:** beispielsweise JPEG oder PNG
- **Breite und Höhe:** Originalabmessungen in Pixeln
- **Dateigröße:** Größe des S3-Objekts in Bytes
- **Helligkeit:** Mittelwert der Graustufen
- **Kontrast:** Standardabweichung der Graustufen
- **Schärfe:** vereinfachte Kantenstärke über einen Edge-Filter
- **durchschnittliche Farbe:** RGB-Mittelwerte
- **Qualitätswert:** gewichtete Kombination der Einzelwerte

### Qualitätsklassen

| Klasse | Qualitätswert | Bedeutung |
|---|---:|---|
| `good` | mindestens 70 | technisch wahrscheinlich gut verwendbar |
| `acceptable` | 45 bis 69,99 | verwendbar, aber manuelle Prüfung sinnvoll |
| `needs_review` | unter 45 | vor Veröffentlichung manuell prüfen |

Die Schwellenwerte sind bewusst einfach, transparent und für den Studienprototypen nachvollziehbar. Sie ersetzen keine fachliche Qualitätsprüfung im Produktivbetrieb.

## 6. Datenmodell

Für jedes verarbeitete Bild wird ein DynamoDB-Element mit `image_id` als Partition Key gespeichert. Es enthält unter anderem:

```json
{
  "image_id": "produkte/testbild.jpg",
  "bucket": "privater-s3-bucket",
  "format": "JPEG",
  "width": 1920,
  "height": 1080,
  "object_size_bytes": 245678,
  "brightness": 128.42,
  "contrast": 46.13,
  "sharpness": 31.72,
  "quality_score": 68.54,
  "quality": "acceptable",
  "average_color_rgb": [132.1, 119.4, 108.7],
  "processed_at": "UTC-Zeitstempel"
}
```

## 7. Sicherheit und Datenschutz

- Der S3-Bucket ist privat.
- Öffentlicher Zugriff wird vollständig blockiert.
- S3 und DynamoDB verwenden serverseitige Verschlüsselung.
- Lambda darf nur das benötigte S3-Objekt lesen und in die definierte DynamoDB-Tabelle schreiben.
- AWS-Zugangsdaten werden ausschließlich lokal über das AWS-Profil verwendet.
- Zugangsdaten, Terraform-State und lokale Variablen werden nicht in Git versioniert.
- Testbilder werden durch eine S3-Lifecycle-Regel nach sieben Tagen gelöscht.
- Für den ersten Test werden nur eigene oder rechtmäßig verwendbare Bilder ohne Personen, Gesichter, Kennzeichen oder private Dokumente verwendet.

Die Maßnahmen unterstützen einen DSGVO-bewussten Studienprototypen. Eine vollständige DSGVO-Konformität für einen echten Geschäftsbetrieb erfordert zusätzlich unter anderem Rechtsgrundlage, Auftragsverarbeitung, Rollen- und Zugriffskonzept, Löschkonzept und organisatorische Prozesse.

## 8. Kostenkontrolle

Die Architektur verwendet keine EC2-Instanz, kein NAT-Gateway und keine RDS-Datenbank. Lambda wird mit 128 MB Speicher, 30 Sekunden Timeout und maximal einer parallelen Ausführung betrieben.

Weitere Begrenzungen:

- maximale Bildgröße in Lambda: 10 MB,
- nur kleine Testbilder für die Demonstration,
- S3-Lifecycle nach sieben Tagen,
- SQS-DLQ-Aufbewahrung für 24 Stunden,
- CloudWatch-Logs-Aufbewahrung für sieben Tage,
- `PAY_PER_REQUEST` für DynamoDB.

Der Free Plan beziehungsweise Free Tier ist keine absolute Kosten-Garantie. Vor und nach jedem Test werden Kostenanzeige, Guthaben und vorhandene Ressourcen kontrolliert. Nach der Demonstration wird `terraform destroy` ausgeführt.

## 9. Bereitstellung und Testplan

1. AWS-Profil und Region prüfen.
2. Lokale Variablen aus `terraform.tfvars.example` erstellen.
3. Lambda-Paket mit Pillow bauen.
4. Python-Test und Terraform-Validierung ausführen.
5. `terraform plan` erstellen und ausschließlich erwartete Ressourcen prüfen.
6. Infrastruktur mit `terraform apply` bereitstellen.
7. Ein kleines, geeignetes Testbild in den ausgegebenen S3-Bucket hochladen.
8. CloudWatch-Log und DynamoDB-Ergebnis kontrollieren.
9. Screenshots als Nachweis für die Präsentation aufnehmen.
10. Infrastruktur mit `terraform destroy` entfernen.

## 10. Erfolgskriterien

Die Umsetzung gilt als erfolgreich, wenn:

- Terraform ohne Validierungsfehler ist,
- das Lambda-Paket `handler.py` und Pillow enthält,
- der lokale Bildanalyse-Test erfolgreich ist,
- ein S3-Upload Lambda automatisch startet,
- ein gültiges DynamoDB-Ergebnis erzeugt wird,
- ein fehlerhaftes Ereignis zur SQS-DLQ weitergeleitet werden kann,
- die Sicherheits- und Kostenmaßnahmen dokumentiert sind,
- die Infrastruktur nach dem Test wieder vollständig gelöscht wird.

## 11. Grenzen und mögliche Erweiterungen

Die heuristische Bewertung ist kein trainiertes Machine-Learning-Modell und kann die Qualität eines Bildes nicht in jedem Fall zuverlässig beurteilen. Die Gewichte und Schwellenwerte müssen für einen produktiven Einsatz mit realen Beispieldaten kalibriert werden.

Mögliche spätere Erweiterungen sind:

- Weboberfläche für Upload und Ergebnisanzeige,
- gespeicherte Vorschaubilder,
- konfigurierbare Qualitätsgrenzen,
- Amazon Rekognition für Objekterkennung,
- Texterkennung mit einem geeigneten AWS-Dienst,
- CloudWatch-Alarme und ein Dashboard.

Diese Erweiterungen gehören nicht zum aktuellen Minimalumfang und werden nur umgesetzt, wenn Kosten, Region und Berechtigungen vorher eindeutig geklärt sind.

## 12. Quellen und Dokumentationsgrenzen

Die technischen Grundlagen und verwendeten Dienste sind in
[`REFERENCES.md`](REFERENCES.md) verzeichnet. Aussagen über eine erfolgreiche
Bereitstellung oder gemessene Kosten dürfen erst nach Durchführung des
beschriebenen Testplans ergänzt werden. Platzhalter oder nicht durchgeführte
Arbeitsschritte werden nicht als Ergebnisse ausgegeben.

Dieses Konzeptblatt dokumentiert die technische Lösung, ersetzt aber nicht den
formalen IU-Projektbericht. Für die Prüfungsabgabe müssen insbesondere die
geforderte Gliederung, die Quellenangaben im Fließtext, das Literaturverzeichnis
und die elektronische eidesstattliche Erklärung nach den IU-Vorgaben separat
erstellt bzw. abgegeben werden.
