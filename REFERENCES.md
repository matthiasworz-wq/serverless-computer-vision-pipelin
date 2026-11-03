# Quellen und technische Referenzen

Dieses Verzeichnis dokumentiert die Quellen, die für die technische Konzeption
und die Implementierung dieses öffentlichen Repositorys verwendet werden. Die
Links verweisen auf die offiziellen Dokumentationen oder auf die im Projekt
bereitgestellten IU-Unterlagen. Zugriff: 3. November 2026.

## IU-Vorgaben

- IU Prüfungsamt: *Prüfungsleitfaden zur Erstellung eines Projektberichts*,
  bereitgestellte PDF-Unterlage, Version im Dokument vom 4. November 2025.
- IU Prüfungsamt: *Vermeidung eines Plagiats*, bereitgestellte PDF-Unterlage,
  Version im Dokument vom 4. November 2025.

Die IU-Unterlagen werden nicht in das öffentliche Repository kopiert. Sie dienen
als Kriterien für die separate Prüfungsabgabe. Wörtliche oder sinngemäße
Übernahmen aus fremden Quellen müssen im einzureichenden Projektbericht nach dem
aktuellen IU-Zitierleitfaden im Fließtext und im Literaturverzeichnis belegt
werden.

## Technische Quellen

- AWS: [Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- AWS: [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- AWS: [Amazon DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
- AWS: [Amazon SQS Developer Guide](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- AWS: [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- Terraform Registry: [AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- Python Packaging User Guide: [Installing packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)
- Pillow documentation: [Pillow handbook](https://pillow.readthedocs.io/en/stable/)

## Projektinterne Provenienz

- `lambda/handler.py`: eigene Implementierung der deterministischen
  Bildqualitätsheuristik.
- `*.tf`: eigene Terraform-Konfiguration für den in README und Konzeptblatt
  beschriebenen Studienprototyp.
- `tools/generate_phase2_presentation.py`: eigene Generierung der
  Präsentationsfolien.

Die technischen Quellen erklären die verwendeten Dienste und Werkzeuge. Die
konkreten Schwellenwerte, Gewichtungen und Ressourcengrenzen sind
projektbezogene Entwurfsentscheidungen und werden im Konzeptblatt begründet.
