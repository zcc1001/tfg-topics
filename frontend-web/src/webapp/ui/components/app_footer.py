import streamlit as st

from webapp.ui.i18n import _


def render_app_footer() -> None:
    css = """
        <style>
            [data-testid="stAppViewContainer"] {
                --app-sidebar-width: 0rem;
            }

            [data-testid="stAppViewContainer"]:has(
                section[data-testid="stSidebar"][aria-expanded="true"]
            ) {
                --app-sidebar-width: 21rem;
            }

            .app-footer {
                position: relative;
                left: 50%;
                right: 50%;
                width: calc(100vw - var(--app-sidebar-width));
                margin-left: calc(-50vw + (var(--app-sidebar-width) / 2));
                margin-right: calc(-50vw + (var(--app-sidebar-width) / 2));
                margin-top: 3rem;
                padding: 1.8rem 0;
                border-top: 1px solid rgba(49, 51, 63, 0.1);
                background:
                    linear-gradient(135deg, #fbfdff 0%, #f4f8fc 52%, #edf3f9 100%);
                color: #334155;
            }

            .app-footer__inner {
                max-width: min(
                    1200px,
                    calc(100vw - var(--app-sidebar-width) - 3rem)
                );
                margin: 0 auto;
                padding: 0 1.5rem;
                display: grid;
                grid-template-columns: minmax(0, 1.4fr) minmax(260px, 0.9fr);
                gap: 1.5rem;
                align-items: start;
            }

            .app-footer__lead {
                position: relative;
                padding-left: 1.1rem;
            }

            .app-footer__lead::before {
                content: "";
                position: absolute;
                top: 0.15rem;
                left: 0;
                width: 0.28rem;
                height: 3.9rem;
                border-radius: 999px;
                background: linear-gradient(180deg, #0f766e 0%, #2563eb 100%);
            }

            .app-footer__eyebrow {
                margin: 0 0 0.45rem 0;
                color: #0f766e;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .app-footer__title {
                margin: 0 0 0.55rem 0;
                color: #0f172a;
                font-size: 1.25rem;
                font-weight: 700;
                line-height: 1.2;
            }

            .app-footer__description {
                margin: 0;
                max-width: 46rem;
                color: #475569;
                font-size: 1rem;
                line-height: 1.6;
            }

            .app-footer__panel {
                padding: 1rem 1.1rem;
                border: 1px solid rgba(37, 99, 235, 0.1);
                border-radius: 1rem;
                background: rgba(255, 255, 255, 0.72);
                box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
                backdrop-filter: blur(6px);
            }

            .app-footer__panel-title {
                margin: 0 0 0.85rem 0;
                color: #0f172a;
                font-size: 0.92rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }

            .app-footer__meta-row {
                display: grid;
                grid-template-columns: 7rem 1fr;
                gap: 0.75rem;
                padding: 0.45rem 0;
                border-bottom: 1px solid rgba(148, 163, 184, 0.18);
                align-items: start;
            }

            .app-footer__meta-row:last-child {
                border-bottom: none;
                padding-bottom: 0;
            }

            .app-footer__label {
                color: #0f172a;
                font-size: 0.88rem;
                font-weight: 700;
            }

            .app-footer__value {
                color: #475569;
                font-size: 0.9rem;
                line-height: 1.45;
                min-width: 0;
                overflow-wrap: anywhere;
                word-break: break-word;
            }

            .app-footer__link {
                color: #2563eb;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.2s ease;
            }

            .app-footer__link:hover {
                color: #1d4ed8;
                text-decoration: underline;
            }

            @media (max-width: 820px) {
                .app-footer__inner {
                    grid-template-columns: 1fr;
                }

                .app-footer__lead {
                    padding-left: 0.9rem;
                }

                .app-footer__lead::before {
                    height: 100%;
                }

                .app-footer__meta-row {
                    grid-template-columns: 1fr;
                    gap: 0.15rem;
                }
            }
        </style>
        """

    html = f"""
        <div class="app-footer">
            <div class="app-footer__inner">
                <div class="app-footer__lead">
                    <p class="app-footer__eyebrow">{_("footer.eyebrow")}</p>
                    <p class="app-footer__title">
                        {_("footer.title")}
                    </p>
                    <p class="app-footer__description">
                        {_("footer.description")}
                    </p>
                </div>
                <div class="app-footer__panel">
                    <p class="app-footer__panel-title">{_("footer.panel_title")}</p>
                    <div class="app-footer__meta-row">
                        <span class="app-footer__label">
                                {_("footer.author_label")}</span>
                        <span class="app-footer__value">
                            Zeldan Javier Campos Cordero
                        </span>
                    </div>
                    <div class="app-footer__meta-row">
                        <span class="app-footer__label">{_("footer.tutor_label")}</span>
                        <span class="app-footer__value">Carlos López Nozal</span>
                    </div>
                    <div class="app-footer__meta-row">
                        <span class="app-footer__label">
                                    {_("footer.center_label")}</span>
                        <span class="app-footer__value">Universidad de Burgos</span>
                    </div>
                    <div class="app-footer__meta-row">
                        <span class="app-footer__label">
                                    {_("footer.course_label")}</span>
                        <span class="app-footer__value">2025/2026</span>
                    </div>
                    <div class="app-footer__meta-row">
                        <span class="app-footer__label">{_("footer.repo_label")}</span>
                        <span class="app-footer__value">
                            <a
                                class="app-footer__link"
                                href="https://github.com/zcc1001/tfg-topics"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                github.com/zcc1001/tfg-topics
                            </a>
                        </span>
                    </div>
                    <div class="app-footer__meta-row">
                        <span class="app-footer__label">{_("footer.wiki_label")}</span>
                        <span class="app-footer__value">
                            <a
                                class="app-footer__link"
                                href="https://github.com/zcc1001/tfg-topics/wiki"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {_("footer.wiki_link")}
                            </a>
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """
    st.markdown(css + html, unsafe_allow_html=True)
