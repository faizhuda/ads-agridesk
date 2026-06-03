"""Tests for PDFGenerator renderer dispatch and the ABC class hierarchy (IMP-01).

These tests mock the storage layer so no real files are written to disk.
They verify:
- Known template names resolve to the correct concrete renderer.
- Unknown template names fall back to GenericTemplateRenderer.
- The injectable registry replaces the default registry cleanly.
- GenericTemplateRenderer uses the injected name as template_name.
- _DrawUtils helpers behave correctly.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.utils.pdf_generator import (
    GenericTemplateRenderer,
    PDFGenerator,
    SuratKeteranganAktifRenderer,
    SuratPembatalanMataKuliahRenderer,
    TEMPLATE_RENDERERS,
    TemplatePDFRenderer,
    _DrawUtils,
)


# ---------------------------------------------------------------------------
# Module-level registry
# ---------------------------------------------------------------------------

class TestTemplateRegistry:
    def test_registry_contains_keterangan_aktif(self):
        assert "Surat Keterangan Aktif Kuliah" in TEMPLATE_RENDERERS

    def test_registry_contains_pembatalan(self):
        assert "Surat Pembatalan Mata Kuliah" in TEMPLATE_RENDERERS

    def test_registry_values_are_renderer_instances(self):
        for renderer in TEMPLATE_RENDERERS.values():
            assert isinstance(renderer, TemplatePDFRenderer)

    def test_keterangan_aktif_is_correct_type(self):
        assert isinstance(
            TEMPLATE_RENDERERS["Surat Keterangan Aktif Kuliah"],
            SuratKeteranganAktifRenderer,
        )

    def test_pembatalan_is_correct_type(self):
        assert isinstance(
            TEMPLATE_RENDERERS["Surat Pembatalan Mata Kuliah"],
            SuratPembatalanMataKuliahRenderer,
        )


# ---------------------------------------------------------------------------
# PDFGenerator dispatcher
# ---------------------------------------------------------------------------

class TestPDFGeneratorDispatch:
    def _make_mock_renderer(self, return_value="uploads/fake.pdf"):
        renderer = MagicMock(spec=TemplatePDFRenderer)
        renderer.render.return_value = return_value
        return renderer

    def test_known_template_calls_registered_renderer(self):
        mock_renderer = self._make_mock_renderer()
        gen = PDFGenerator(renderer_registry={"My Template": mock_renderer})

        gen.generate_from_template("My Template", {"key": "val"}, "out.pdf")

        mock_renderer.render.assert_called_once_with({"key": "val"}, None, "out.pdf", signature_hash=None)

    def test_known_template_passes_signature_path(self):
        mock_renderer = self._make_mock_renderer()
        gen = PDFGenerator(renderer_registry={"T": mock_renderer})

        gen.generate_from_template("T", {}, "f.pdf", signature_path="/sig.png")

        _, call_kwargs = mock_renderer.render.call_args
        # called positionally: (fields, signature_path, filename)
        assert mock_renderer.render.call_args[0][1] == "/sig.png"

    def test_unknown_template_falls_back_to_generic(self):
        gen = PDFGenerator(renderer_registry={})  # empty — no known templates

        captured = {}

        def fake_render(fields, sig_path, filename, signature_hash=None):
            captured["renderer_name"] = gen._renderers.get("Unknown") or GenericTemplateRenderer("Unknown")
            return "uploads/generic.pdf"

        # Patch GenericTemplateRenderer.render to avoid actual PDF generation
        with patch.object(GenericTemplateRenderer, "render", side_effect=fake_render) as mock_render:
            gen.generate_from_template("Unknown Template", {}, "out.pdf")
            mock_render.assert_called_once()

    def test_returns_storage_path_from_renderer(self):
        mock_renderer = self._make_mock_renderer("uploads/my_output.pdf")
        gen = PDFGenerator(renderer_registry={"T": mock_renderer})

        result = gen.generate_from_template("T", {}, "out.pdf")
        assert result == "uploads/my_output.pdf"

    def test_default_registry_is_used_when_none_provided(self):
        gen = PDFGenerator()
        assert gen._renderers is TEMPLATE_RENDERERS

    def test_injected_registry_replaces_default(self):
        custom = {"Custom": MagicMock(spec=TemplatePDFRenderer)}
        gen = PDFGenerator(renderer_registry=custom)
        assert gen._renderers is custom
        assert "Surat Keterangan Aktif Kuliah" not in gen._renderers

    def test_two_generators_share_same_default_registry(self):
        g1 = PDFGenerator()
        g2 = PDFGenerator()
        assert g1._renderers is g2._renderers


# ---------------------------------------------------------------------------
# GenericTemplateRenderer
# ---------------------------------------------------------------------------

class TestGenericTemplateRenderer:
    def test_template_name_matches_constructor_arg(self):
        renderer = GenericTemplateRenderer("Surat Bebas")
        assert renderer.template_name == "Surat Bebas"

    def test_default_template_name_is_surat(self):
        renderer = GenericTemplateRenderer()
        assert renderer.template_name == "Surat"

    def test_is_subclass_of_template_renderer(self):
        assert issubclass(GenericTemplateRenderer, TemplatePDFRenderer)

    def test_render_calls_upload(self, tmp_path):
        """GenericTemplateRenderer.render() should call storage_service.upload_file."""
        renderer = GenericTemplateRenderer("Test Surat")
        fake_path = "uploads/fake_generic.pdf"

        with patch("app.utils.storage.storage_service") as mock_storage:
            mock_storage.upload_file.return_value = fake_path
            result = renderer.render({"field1": "value1"}, None, "out.pdf")

        mock_storage.upload_file.assert_called_once()
        assert result == fake_path


# ---------------------------------------------------------------------------
# Concrete renderers — template_name attribute
# ---------------------------------------------------------------------------

class TestConcreteRendererNames:
    def test_keterangan_aktif_template_name(self):
        assert SuratKeteranganAktifRenderer.template_name == "Surat Keterangan Aktif Kuliah"

    def test_pembatalan_template_name(self):
        assert SuratPembatalanMataKuliahRenderer.template_name == "Surat Pembatalan Mata Kuliah"


# ---------------------------------------------------------------------------
# _DrawUtils helpers
# ---------------------------------------------------------------------------

class TestDrawUtils:
    def test_format_label_replaces_underscores(self):
        assert _DrawUtils._format_label("nama_lengkap") == "Nama Lengkap"

    def test_format_label_title_cases(self):
        assert _DrawUtils._format_label("jurusan") == "Jurusan"

    def test_wrapped_lines_returns_list(self):
        lines = _DrawUtils._wrapped_lines("Hello world", font_size=10, max_width=200)
        assert isinstance(lines, list)
        assert len(lines) >= 1

    def test_wrapped_lines_splits_long_text(self):
        long_text = "A " * 100
        lines = _DrawUtils._wrapped_lines(long_text, font_size=10, max_width=200)
        assert len(lines) > 1

    def test_wrapped_lines_preserves_short_text(self):
        lines = _DrawUtils._wrapped_lines("Short", font_size=10, max_width=500)
        assert lines == ["Short"]
