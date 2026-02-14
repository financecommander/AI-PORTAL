"""Sidebar UI component for FinanceCommander AI Portal."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import streamlit as st

from auth.authenticator import authenticate, get_current_user, logout
from specialists.manager import SpecialistManager


def render_sidebar():
    """Render the sidebar with authentication and specialist selection."""
    with st.sidebar:
        st.title("💰 FinanceCommander AI")

        # Authentication section
        if not st.session_state.get("authenticated", False):
            _render_auth_form()
        else:
            _render_user_info()

        # Specialist selection
        if st.session_state.get("authenticated", False):
            _render_specialist_selector()
            _render_specialist_manager()
            _render_conversation_export()

            # Show rate limit info
            bucket = st.session_state.get("portal_rate_bucket")
            if bucket is not None:
                remaining = bucket.remaining
                st.caption(f"🪣 API calls remaining: **{remaining}** / {bucket.capacity}")


def _render_auth_form():
    """Render authentication form."""
    st.subheader("🔐 Authentication")

    with st.form("auth_form"):
        email = st.text_input("Email address", placeholder="user@financecommander.com")
        submitted = st.form_submit_button("Authenticate")

        if submitted:
            result = authenticate(email)
            if result.success:
                st.session_state.authenticated = True
                st.session_state.user_email = result.user_email
                st.success(f"Welcome, {result.user_email}!")
                st.rerun()
            else:
                st.error(result.error_message)


def _render_user_info():
    """Render authenticated user info and logout."""
    user_email = get_current_user()
    if user_email:
        st.subheader("👤 User")
        st.write(f"**{user_email}**")

        if st.button("Logout"):
            logout()
            st.rerun()


def _render_specialist_selector():
    """Render specialist selection dropdown."""
    st.subheader("🎯 Specialist")

    manager = SpecialistManager()
    specialists = manager.list()

    if specialists:
        specialist_names = [s.name for s in specialists]
        selected_name = st.selectbox(
            "Choose a specialist:",
            specialist_names,
            key="specialist_selector",
        )

        # Store selected specialist in session state
        selected_specialist = next(
            (s for s in specialists if s.name == selected_name), None
        )
        st.session_state.selected_specialist = selected_specialist

        if selected_specialist:
            st.caption(f"**{selected_specialist.name}**")
            st.caption(selected_specialist.description)
    else:
        st.warning("No specialists available")


def _render_specialist_manager():
    """Render the specialist CRUD management expander."""
    with st.expander("⚙️ Manage Specialists"):
        tab_add, tab_edit, tab_delete = st.tabs(["Add", "Edit", "Delete"])

        manager = SpecialistManager()

        # ── Add ──
        with tab_add:
            with st.form("add_specialist_form"):
                name = st.text_input("Name", key="add_name")
                description = st.text_input("Description", key="add_desc")
                provider = st.selectbox(
                    "Provider",
                    ["openai", "anthropic", "google"],
                    key="add_provider",
                )
                model = st.text_input("Model", value="gpt-4o", key="add_model")
                system_prompt = st.text_area(
                    "System prompt",
                    value="You are a helpful AI assistant.",
                    key="add_prompt",
                )
                temperature = st.slider(
                    "Temperature", 0.0, 2.0, 0.7, 0.1, key="add_temp"
                )
                max_tokens = st.number_input(
                    "Max tokens", 256, 8192, 2048, key="add_tokens"
                )
                base_url = st.text_input("Base URL (optional)", key="add_url")
                submitted = st.form_submit_button("Create Specialist")

                if submitted:
                    errors = manager.validate_specialist(
                        name=name,
                        provider=provider,
                        model=model,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        base_url=base_url,
                        description=description,
                    )
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        manager.create(
                            name=name.strip(),
                            description=description,
                            provider=provider,
                            model=model,
                            system_prompt=system_prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            base_url=base_url,
                        )
                        st.success(f"Created specialist '{name}'")
                        st.rerun()

        # ── Edit ──
        with tab_edit:
            specialists = manager.list()
            if not specialists:
                st.info("No specialists to edit.")
            else:
                edit_names = [s.name for s in specialists]
                edit_sel = st.selectbox(
                    "Select specialist to edit", edit_names, key="edit_sel"
                )
                spec = next((s for s in specialists if s.name == edit_sel), None)
                if spec:
                    with st.form("edit_specialist_form"):
                        name = st.text_input("Name", value=spec.name, key="edit_name")
                        description = st.text_input(
                            "Description", value=spec.description, key="edit_desc"
                        )
                        prov_idx = (
                            ["openai", "anthropic", "google"].index(spec.provider)
                            if spec.provider in ["openai", "anthropic", "google"]
                            else 0
                        )
                        provider = st.selectbox(
                            "Provider",
                            ["openai", "anthropic", "google"],
                            index=prov_idx,
                            key="edit_provider",
                        )
                        model = st.text_input(
                            "Model", value=spec.model, key="edit_model"
                        )
                        system_prompt = st.text_area(
                            "System prompt",
                            value=spec.system_prompt,
                            key="edit_prompt",
                        )
                        temperature = st.slider(
                            "Temperature",
                            0.0,
                            2.0,
                            spec.temperature,
                            0.1,
                            key="edit_temp",
                        )
                        max_tokens = st.number_input(
                            "Max tokens",
                            256,
                            8192,
                            spec.max_tokens,
                            key="edit_tokens",
                        )
                        base_url = st.text_input(
                            "Base URL", value=spec.base_url or "", key="edit_url"
                        )
                        submitted = st.form_submit_button("Update Specialist")

                        if submitted:
                            errors = manager.validate_specialist(
                                name=name,
                                provider=provider,
                                model=model,
                                system_prompt=system_prompt,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                base_url=base_url,
                                description=description,
                                exclude_id=spec.id,
                            )
                            if errors:
                                for err in errors:
                                    st.error(err)
                            else:
                                manager.update(
                                    spec.id,
                                    name=name.strip(),
                                    description=description,
                                    provider=provider,
                                    model=model,
                                    system_prompt=system_prompt,
                                    temperature=temperature,
                                    max_tokens=max_tokens,
                                    base_url=base_url,
                                )
                                st.success(f"Updated specialist '{name}'")
                                st.rerun()

        # ── Delete ──
        with tab_delete:
            specialists = manager.list()
            if not specialists:
                st.info("No specialists to delete.")
            else:
                del_names = [s.name for s in specialists]
                del_sel = st.selectbox(
                    "Select specialist to delete", del_names, key="del_sel"
                )
                spec = next((s for s in specialists if s.name == del_sel), None)
                if spec and st.button(
                    f"🗑️ Delete '{spec.name}'", key="del_btn", type="primary"
                ):
                    manager.delete(spec.id)
                    st.success(f"Deleted specialist '{spec.name}'")
                    st.rerun()


def _render_conversation_export():
    """Render conversation export download button."""
    specialist = st.session_state.get("selected_specialist")
    if not specialist:
        return
    hk = f"portal_chat_history_{specialist.id}"
    history = st.session_state.get(hk, [])
    if not history:
        return

    export = {
        "specialist_id": specialist.id,
        "specialist_name": specialist.name,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "messages": history,
    }
    st.download_button(
        "📥 Export Conversation",
        data=json.dumps(export, indent=2),
        file_name=f"chat_{specialist.name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        key="export_btn",
    )