from processing.application.services.latex_text_processor import LatexTextProcessor


class TestLatexTextProcessor:
    """Test suite for the LatexTextProcessor class."""

    def test_clean_empty_text(self) -> None:
        """Test that cleaning an empty string results in an empty string."""
        assert LatexTextProcessor.clean("") == ""

    def test_clean_html_remnants(self) -> None:
        """Test that HTML tags are correctly removed."""
        text = "<p>This is <b>HTML</b>.</p>"
        expected = "this is html"
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_sectioning_commands(self) -> None:
        r"""Test removal of LaTeX sectioning commands (e.g., \chapter, \section)."""
        text = (
            r"\chapter{Introduction}\section{Background}"
            r"\subsection*{Details} Some text."
        )
        expected = "some text"
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_latex_environments(self) -> None:
        """Test removal of entire LaTeX environments (e.g., figure, tabular)."""
        text = r"\begin{figure}Content\end{figure}" r"\begin{tabular}Data\end{tabular}"
        expected = ""
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_math_expressions(self) -> None:
        """Test removal of both inline and display math expressions."""
        text = "An equation $$E=mc^2$$ and inline math $a^2+b^2=c^2$."
        expected = "an equation and inline math"
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_generic_latex_commands(self) -> None:
        """Test removal of generic commands whose arguments should also be removed."""
        text = r"\label{fig:my_fig}\cite{knuth1984} Some text."
        expected = "some text"
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_residual_latex_structural_tokens(self) -> None:
        """Test removal of concatenated structural tokens like 'beginsection'."""
        text = "beginsection endsection"
        expected = ""
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_table_formatting_commands(self) -> None:
        """Test removal of table-specific formatting commands."""
        text = r"\toprule \midrule \bottomrule some data"
        expected = "some data"
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_concatenated_latex_command_artifacts(self) -> None:
        """Test removal of command prefixes from concatenated words."""
        text = "sectiontitle subsectionanother"
        expected = "title another"

        assert LatexTextProcessor.clean(text) == expected

    def test_normalize_unicode(self) -> None:
        """Test that unicode characters and accents are normalized."""
        text = "café niño"
        expected = "cafe nino"
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_non_alphabetic_characters(self) -> None:
        """Test that non-alphabetic characters are removed."""
        text = "This is a test-1,2,3."
        expected = "this is a test"
        assert LatexTextProcessor.clean(text) == expected

    def test_remove_common_academic_structural_words(self) -> None:
        """Test removal of common structural words found in academic papers."""
        text = "Figure 1 shows a table with data. Pagina 2."
        expected = "shows a with data"
        assert LatexTextProcessor.clean(text) == expected

    def test_normalize_whitespace_and_lowercase(self) -> None:
        """Test that whitespace is normalized and the text is lowercased."""
        text = "  This   is  a  TEST  .  "
        expected = "this is a test"
        assert LatexTextProcessor.clean(text) == expected

    def test_clean_integration(self) -> None:
        """Perform an integration test with a complete LaTeX document."""
        latex_text = r"""
        \documentclass{article}
        \usepackage[utf8]{inputenc}
        \usepackage{amsmath}

        \title{An Example LaTeX Document}
        \author{John Doe}
        \date{\today}

        \begin{document}

        \maketitle

        \section{Introduction}
        This is the first section. We will discuss the importance of cleaning
        text for NLP tasks.
        Here is an equation: $E = mc^2$.

        \subsection{Subsection}
        This is a subsection with some \textbf{bold} and \textit{italic} text.
        Let's add a list:
        \begin{itemize}
            \item Item 1
            \item Item 2
        \end{itemize}

        And a table:
        \begin{table}[h!]
            \centering
            \begin{tabular}{|c|c|}
                \hline
                Header 1 & Header 2 \\
                \hline
                Data 1 & Data 2 \\
                \hline
            \end{tabular}
            \caption{A simple table.}
            \label{tab:simple_table}
        \end{table}

        \section*{Conclusion}
        In conclusion, LaTeX documents can be cleaned effectively.
        Accented characters like á, é, í, ó, ú, ñ should be handled.
        Also, symbols like @, #, $, %, &, / should be removed.

        \end{document}
        """
        expected_output = (
            "an example latex document john doe this is the first we will discuss the "
            "importance of cleaning text for nlp tasks here is an equation this is a "
            "with some bold and italic text let s add a list and a in conclusion latex "
            "documents can be cleaned effectively accented characters like a e i o u n "
            "should be handled also symbols like should be removed"
        )
        cleaned_text = LatexTextProcessor.clean(latex_text)
        assert cleaned_text == expected_output
