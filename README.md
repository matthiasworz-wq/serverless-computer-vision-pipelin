# Serverless Computer Vision Pipeline auf AWS

Dieses Projekt ist die Umsetzung von **Aufgabe 2: Entwicklung einer eigenen kreativen Cloud-Lösung** im IU-Kurs *Cloud Programming*. Ein Bild wird in einen privaten Amazon-S3-Bucket hochgeladen, automatisch durch AWS Lambda mit Pillow auf Bildqualität geprüft und als strukturierte Metadaten in Amazon DynamoDB gespeichert.

## 1. Realistisches Szenario und Ziel

Ein kleiner Onlinehändler für gebrauchte Elektronik erhält etwa 100 Bild-Uploads pro Monat. Die Bilder sollen automatisch auf technische Qualität geprüft werden, damit Mitarbeitende ungeeignete Produktfotos vor der Veröffentlichung erkennen. Das fiktive Unternehmen hat ein kleines IT-Team, möchte keinen Server dauerhaft betreiben und setzt ein monatliches Testbudget von höchstens 1 EUR voraus.

Die priorisierten Anforderungen sind:

1. **Kostenkontrolle:** keine dauerhaft laufenden Server; wenige Testbilder; automatische Aufräumregel.
2. **Sicherheit:** privater S3-Bucket, Verschlüsselung, Least-Privilege-IAM und keine Zugangsdaten im Repository.
3. **Automatisierung:** S3-Upload löst die Verarbeitung ohne manuellen Eingriff aus.
4. **Reproduzierbarkeit:** alle Infrastrukturressourcen werden mit Terraform beschrieben.
5. **Skalierbarkeit:** Lambda und die verwalteten AWS-Dienste skalieren ohne eigene Serververwaltung.

Die Kostenfreiheit ist nicht absolut garantiert: AWS Free Tier, Kontingente, Region, Kontostatus und Laufzeit müssen vor jedem Test geprüft werden. Für die praktische Durchführung wird deshalb nur ein kleines Bild verwendet und die Infrastruktur nach dem Test mit `terraform destroy` entfernt.

## 2. Architektur und Datenfluss

```text
Client
  │ Upload (JPEG/JPG/PNG)
  ▼
Privater Amazon-S3-Bucket
  │ ObjectCreated-Event
  ▼
AWS Lambda (Python 3.12)
  ├── Pillow: Format, Größe, Helligkeit, Kontrast und Schärfe
  ├── Amazon DynamoDB: PutItem mit Analyse-Metadaten
  └── SQS-DLQ bei fehlgeschlagener Verarbeitung
```

Die Lambda-Funktion verarbeitet auch mehrere Datensätze in einem Event, dekodiert URL-kodierte S3-Schlüssel, lädt das Bild aus S3 und berechnet lokale Bildqualitätsmetriken. Gespeichert werden unter anderem Format, Abmessungen, Dateigröße, durchschnittliche Farbe, Helligkeit, Kontrast, Schärfe und eine Qualitätsklassifizierung (`good`, `acceptable` oder `needs_review`). Testbilder werden nach sieben Tagen automatisch aus S3 entfernt. CloudWatch-Logs werden sieben Tage aufbewahrt.

## 3. Repository-Struktur

| Datei | Zweck |
|---|---|
| `providers.tf` | Terraform- und AWS-Provider |
| `variables.tf` | Konfigurierbare Region, Namen und Profil |
| `terraform.tfvars.example` | Vorlage für lokale Werte |
| `s3.tf` | Privater, verschlüsselter S3-Bucket, Lifecycle und Public-Access-Schutz |
| `lambda.tf` | Lambda, S3-Trigger, CloudWatch-Loggruppe und SQS-DLQ |
| `dynamodb.tf` | DynamoDB-Tabelle für Metadaten |
| `iam.tf` | Ausführungsrolle mit begrenzten Berechtigungen |
| `lambda/handler.py` | Python-Verarbeitungslogik |
| `lambda/requirements.txt` | Reproduzierbare Pillow-Abhängigkeit |
| `tools/package_lambda.py` | Erstellt ein AWS-kompatibles Lambda-ZIP mit Pillow |
| `tests/test_image_analysis.py` | Lokaler Test der Bildanalyse |
| `outputs.tf` | Ausgaben nach dem Deployment |

Terraform-State, Pläne, Zugangsdaten und lokale Variablen werden durch `.gitignore` vom Repository ausgeschlossen. Die Datei `.terraform.lock.hcl` wird dagegen versioniert, damit Provider-Versionen reproduzierbar bleiben.

## 4. Voraussetzungen

- AWS-Konto mit ausreichenden IAM-Berechtigungen
- AWS CLI mit einem lokalen Profil, z. B. `terraform`
- Terraform >= 1.5
- Python 3.12 für lokale Syntaxprüfungen
- Internetzugriff beim einmaligen Erstellen des Lambda-Pakets für Pillow

Die AWS-Zugangsdaten werden ausschließlich lokal über AWS CLI/Profile oder Umgebungsvariablen verwendet. Sie gehören niemals in `terraform.tfvars`, den Lambda-Code oder GitHub.

## 5. Sicherer Ablauf für Phase 2

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
# terraform.tfvars bei Bedarf anpassen

terraform init
terraform fmt -check
terraform validate
python tools/package_lambda.py
python -m pytest -q tests/test_image_analysis.py
terraform plan -out phase2.tfplan
```

Den Plan vor der Bereitstellung vollständig prüfen. Nur wenn ausschließlich die erwarteten Ressourcen enthalten sind:

```powershell
terraform apply phase2.tfplan
terraform output
```

Danach genau ein kleines JPEG- oder PNG-Testbild in den ausgegebenen Bucket hochladen. Die Ausführung wird in **CloudWatch Logs** geprüft; das Ergebnis wird in **DynamoDB** kontrolliert. Die SQS-DLQ dient zur Untersuchung fehlgeschlagener Lambda-Aufrufe.

Nach der Dokumentation der Testergebnisse:

```powershell
terraform destroy
```

Anschließend in AWS zusätzlich kontrollieren, dass S3-Bucket, Lambda, DynamoDB-Tabelle, SQS-DLQ und Loggruppe entfernt wurden. Erst danach kann das Repository wieder öffentlich gemacht werden. Offizielle Aufgabenunterlagen und persönliche Bewertungsdokumente sind nicht Bestandteil dieses technischen Repositories.

## 6. Kosten- und Sicherheitsmaßnahmen

- keine EC2-Instanz, kein NAT-Gateway und keine dauerhaft laufende Infrastruktur
- Lambda auf 128 MB, 30 Sekunden und maximal eine parallele Ausführung begrenzt
- S3 nur für JPEG/JPG/PNG-Trigger; Testobjekte werden nach sieben Tagen gelöscht
- SQS-DLQ hält Nachrichten nur 24 Stunden
- CloudWatch-Logs werden sieben Tage aufbewahrt
- S3 und DynamoDB nutzen serverseitige Verschlüsselung
- S3 Public Access Block ist vollständig aktiviert
- Lambda darf nur das erforderliche S3-Objekt lesen, in DynamoDB schreiben und Fehler an die DLQ senden
- Die Bildanalyse läuft lokal in Lambda; es werden keine externen Vision- oder OCR-APIs aufgerufen

Diese Maßnahmen reduzieren das Risiko, ersetzen aber keine Prüfung der AWS-Kostenanzeige und keine Kontrolle der Free-Tier-Grenzen.

## 7. Alternativen und Grenzen

Amazon Rekognition oder Textract wären mögliche Erweiterungen, wenn später Objekt- oder Texterkennung benötigt wird. Ein eigener ML-Service oder EC2 würde mehr Kontrolle geben, aber dauerhaft höhere Betriebs- und Administrationskosten verursachen. Die gewählte Pillow-Analyse ist bewusst unabhängig von regional nicht verfügbaren oder gesperrten KI-Diensten.

Die Lösung ist für einen kontrollierten Studienprototypen ausgelegt. Für einen produktiven Betrieb wären unter anderem zentrale State-Verwaltung, Monitoring/Alarme, Bildgrößenlimits, Verschlüsselung mit kundeneigenem KMS-Schlüssel und eine strengere Trennung von Entwicklungs- und Produktionskonto zu ergänzen.
