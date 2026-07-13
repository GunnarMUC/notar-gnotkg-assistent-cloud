"""Tests für den Invoice Generator und Excel Logger."""

from core.excel_logger import create_audit_log
from core.invoice_generator import generate_invoice


class TestInvoiceGenerator:
    def test_generate_txt(self):
        positions = [
            {
                "kv_number": "21200",
                "description": "Beurkundung",
                "business_value_eur": 385000.0,
                "fee_amount": 1060.0,
                "source_reference": "Ziff. 1",
                "was_overridden": False,
            }
        ]
        notary = {
            "name": "Dr. Test",
            "firm_name": "Notariat Test",
            "address": "Amtsplatz 1, 80331 München",
            "bank_name": "Testbank",
            "iban": "DE12345678901234567890",
        }
        auslagen = {"dokumentenpauschale": 25.0, "post_telekom": 10.0, "sonstige": 0.0}
        content, invoice = generate_invoice(
            positions, notary, output_format="txt", auslagen=auslagen
        )
        text = content.decode("utf-8")
        assert "HONORARRECHNUNG" in text
        assert "Dr. Test" in text
        assert "1,060" in text.replace(".", ",")
        assert "Dokumentenpauschale" in text
        assert invoice.total_net == 1095.0

    def test_generate_docx(self):
        positions = [
            {
                "kv_number": "22114",
                "description": "Elektronischer Vollzug",
                "business_value_eur": None,
                "fee_amount": 15.0,
                "source_reference": "",
                "was_overridden": False,
            }
        ]
        notary = {
            "name": "Dr. Test",
            "firm_name": "Notariat Test",
            "address": "Amtsplatz 1",
            "bank_name": "Testbank",
            "iban": "DE1234567890",
        }
        auslagen = {"dokumentenpauschale": 20.0, "post_telekom": 0.0, "sonstige": 5.0}
        content, invoice = generate_invoice(
            positions, notary, output_format="docx", auslagen=auslagen
        )
        assert len(content) > 100
        assert content[:2] == b"PK"  # DOCX/ZIP magic bytes
        assert invoice.total_net == 40.0

    def test_generate_rtf(self):
        positions = [
            {
                "kv_number": "21200",
                "description": "Beurkundung",
                "business_value_eur": 100000.0,
                "fee_amount": 354.0,
                "source_reference": "",
                "was_overridden": False,
            }
        ]
        notary = {
            "name": "T",
            "firm_name": "K",
            "address": "A",
            "bank_name": "B",
            "iban": "I",
        }
        content, invoice = generate_invoice(positions, notary, output_format="rtf")
        text = content.decode("cp1252", errors="replace")
        assert "HONORARRECHNUNG" in text
        assert r"{\rtf1" in text

    def test_generate_invoice_without_auslagen(self):
        positions = [
            {
                "kv_number": "21200",
                "description": "Beurkundung",
                "business_value_eur": 100000.0,
                "fee_amount": 354.0,
                "source_reference": "",
                "was_overridden": False,
            }
        ]
        notary = {
            "name": "T",
            "firm_name": "K",
            "address": "A",
            "bank_name": "B",
            "iban": "I",
        }
        content, invoice = generate_invoice(positions, notary, output_format="txt")
        assert invoice.total_net == 354.0
        assert invoice.auslagen == {}


class TestExcelLogger:
    def test_create_audit_log(self):
        from core.models import FinalInvoicePosition, GeneratedInvoice, NotaryProfile

        profile = NotaryProfile(name="T", firm_name="K", address="A", bank_name="B", iban="I")
        positions = [
            FinalInvoicePosition(
                kv_number="21200",
                description="Beurkundung",
                business_value_eur=100000.0,
                fee_amount=354.0,
            )
        ]
        invoice = GeneratedInvoice(
            notary=profile,
            positions=positions,
            auslagen={"dokumentenpauschale": 25.0, "post_telekom": 0.0, "sonstige": 5.0},
            total_net=384.0,
            vat_amount=72.96,
            total_gross=456.96,
        )
        excel_bytes = create_audit_log(invoice)
        assert len(excel_bytes) > 100
        assert excel_bytes[:2] == b"PK"  # XLSX/ZIP magic bytes
