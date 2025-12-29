import re
import unicodedata

from bs4 import BeautifulSoup


class LatexTextProcessor:
    """
    Utility class responsible for cleaning and normalizing LaTeX-based
    academic documents for NLP tasks (topic modeling, embeddings, etc.).

    Designed to be reusable across different topic modeling algorithms.
    """

    # --- Pre-compiled Regex Patterns ---

    # Sectioning commands
    # Matches commands like:
    #   \section{Introduction}
    #   \subsection{Y}
    #   \chapter{X}
    _SECTION_CMDS = re.compile(r"\\((sub)*section|chapter)\*?\{[^}]*\}", re.IGNORECASE)

    # Document environment markers
    # Matches:
    #   \begin{document}
    #   \end{document}
    _DOC_ENV = re.compile(r"\\(begin|end)\{document\}", re.IGNORECASE)

    #  Environments to be removed completely (incl. content)
    _ENV_NAMES = "|".join(
        [
            "table",
            "figure",
            "tabular",
            "itemize",
            "enumerate",
            "equation",
            "align",
            "eqnarray",
            "lstlisting",
            "verbatim",
            "center",
        ]
    )

    # Matches the entire block:
    #   \begin{environment}
    #       ... anything inside ...
    #   \end{environment}
    _ENV_PATTERN = re.compile(
        r"\\begin\{(" + _ENV_NAMES + r")\}.*?\\end\{\1\}", re.DOTALL | re.IGNORECASE
    )

    # Math environments
    # Matches display math:
    #   $$ ... $$
    _DISPLAY_MATH = re.compile(r"\$\$.*?\$\$", re.DOTALL)
    _INLINE_MATH = re.compile(r"\$[^$]+\$")

    # Commands whose arguments should be removed
    # Matches commands such as:
    #   \documentclass{article}
    #   \usepackage{amsmath}
    #   \cite{some_reference}
    _NUKE_ARGS_CMDS_NAMES = "|".join(
        ["documentclass", "usepackage", "label", "cite", "date", "maketitle", "item"]
    )
    _NUKE_ARGS_CMDS = re.compile(
        r"\\(" + _NUKE_ARGS_CMDS_NAMES + r")(\[[^\]]*\])?(\{[^}]*\})?", re.IGNORECASE
    )
    #  Generic commands where only the command name is removed
    #   \textbf
    #   \emph
    #   \ref
    _STRIP_CMD = re.compile(r"\\[a-zA-Z]+")

    #  Residual structural tokens
    _RESIDUAL_TOKENS = re.compile(r"\b(begin|end)[a-zA-Z]+\b", re.IGNORECASE)

    #  Table formatting commands
    # Commands commonly found inside tables:
    #   \toprule, \midrule, \bottomrule, etc.
    _TABLE_FORMAT_CMDS = re.compile(
        r"\b(toprule|midrule|bottomrule|cmidrule|addlinespace|otoprule)\b",
        re.IGNORECASE,
    )

    #  Concatenated command artifacts
    _CONCAT_CMDS_PREFIX = re.compile(
        r"\b(section|subsection|chapter|capitulo|textbf|textit|emph)", re.IGNORECASE
    )
    _CONCAT_CMDS_WHOLE = re.compile(r"\b(linebreak|newline)\b", re.IGNORECASE)

    #  Non-alphabetic characters
    # Removes numbers, punctuation, symbols, etc.
    # Keeps only letters and whitespace.
    _NON_ALPHA = re.compile(r"[^a-zA-Z\s]")

    #  Common academic structural words
    # These words appear frequently in academic texts
    # but do not help differentiate topics.
    _ACADEMIC_WORDS_NAMES = "|".join(
        [
            "pagina",
            "capitulo",
            "seccion",
            "subseccion",
            "figura",
            "figure",
            "tabla",
            "table",
            "tablas",
            "comando",
            "ejemplo",
            "nuevo",
            "continua",
            "center",
        ]
    )
    _ACADEMIC_WORDS = re.compile(r"\b(" + _ACADEMIC_WORDS_NAMES + r")\b", re.IGNORECASE)

    # 12. Whitespace normalization
    # Replaces multiple spaces, tabs, or line breaks with a single space.
    _WHITESPACE = re.compile(r"\s+")

    @staticmethod
    def clean(text: str) -> str:
        """
        Cleans and normalizes LaTeX text for NLP tasks.

        Args:
            text (str): Raw LaTeX text.

        Returns:
            str: Cleaned and normalized text.
        """
        if not text:
            return ""

        #  Remove HTML
        text = BeautifulSoup(text, "lxml").get_text()

        # Apply regex substitutions in order
        text = LatexTextProcessor._SECTION_CMDS.sub(" ", text)
        text = LatexTextProcessor._DOC_ENV.sub(" ", text)
        text = LatexTextProcessor._ENV_PATTERN.sub(" ", text)
        text = LatexTextProcessor._DISPLAY_MATH.sub(" ", text)
        text = LatexTextProcessor._INLINE_MATH.sub(" ", text)
        text = LatexTextProcessor._NUKE_ARGS_CMDS.sub(" ", text)
        text = LatexTextProcessor._STRIP_CMD.sub(" ", text)
        text = LatexTextProcessor._RESIDUAL_TOKENS.sub(" ", text)
        text = LatexTextProcessor._TABLE_FORMAT_CMDS.sub(" ", text)
        text = LatexTextProcessor._CONCAT_CMDS_PREFIX.sub(" ", text)
        text = LatexTextProcessor._CONCAT_CMDS_WHOLE.sub(" ", text)

        # Normalize Unicode (remove accents)
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))

        # Remove non-alphabetic chars and structural words
        text = LatexTextProcessor._NON_ALPHA.sub(" ", text)
        text = LatexTextProcessor._ACADEMIC_WORDS.sub(" ", text)

        # Normalize whitespace and lowercase
        text = LatexTextProcessor._WHITESPACE.sub(" ", text).strip().lower()

        return text
