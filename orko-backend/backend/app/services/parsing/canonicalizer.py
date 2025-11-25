from __future__ import annotations

from typing import Any, Dict


def _norm(s: str | None) -> str:
    if not s:
        return ""
    return s.strip().lower()


# Set of canonical domains used by ORKO / eval
_CANONICAL_DOMAINS = {
    "trading",
    "logistics",
    "finance",
    "hr",
    "it_ops",
    "devops",
    "customer_support",
    "operations",
    "analytics",
    "sales",
    "marketing",
    "procurement",
    "manufacturing",
    "legal",
    "retail",
    "energy",
    "healthcare_admin",
    "general_admin",
    "knowledge_work",
}


def _heuristic_domain_from_text(text: str, default: str | None = None) -> str | None:
    """
    Lightweight heuristic domain guess based ONLY on the raw text.

    Mirrors CommandParser._guess_domain, but side-effect free and safe to call
    from canonicalization.
    """
    t = text.lower()

    if any(k in t for k in ["contract", "hedge", "pnl", "hedging", "mt", "shipment"]):
        return "trading"
    if any(k in t for k in ["ship", "vessel", "eta", "load", "port", "truck", "warehouse", "delivery"]):
        return "logistics"
    if any(k in t for k in ["invoice", "cashflow", "pnl", "tax", "budget", "expense"]):
        return "finance"
    if any(k in t for k in ["employee", "onboarding", "vacation", "leave", "hr"]):
        return "hr"
    if any(k in t for k in ["service", "incident", "cluster", "server", "restart", "patch"]):
        return "it_ops"
    if any(k in t for k in ["microservice", "load test", "deploy pipeline", "devops"]):
        return "devops"
    if any(k in t for k in ["ticket", "support case", "escalation"]):
        return "customer_support"
    if any(k in t for k in ["maintenance", "checklist", "operational risk", "incidents", "staffing"]):
        return "operations"
    if any(k in t for k in ["forecast", "demand", "retention", "churn", "analytics"]):
        return "analytics"
    if any(k in t for k in ["opportunity", "pipeline", "win-loss", "sales"]):
        return "sales"
    if any(k in t for k in ["campaign", "marketing", "engagement", "social media"]):
        return "marketing"
    if any(k in t for k in ["purchase order", "suppliers", "vendor", "sourcing"]):
        return "procurement"
    if any(k in t for k in ["machine", "work orders", "plant", "assembly"]):
        return "manufacturing"
    if any(k in t for k in ["nda", "contract", "compliance", "regulation", "legal"]):
        return "legal"
    if any(k in t for k in ["store", "inventory", "stockout", "retail"]):
        return "retail"
    if any(k in t for k in ["grid", "outage", "energy", "renewable"]):
        return "energy"
    if any(k in t for k in ["patient", "claims", "lab results"]):
        return "healthcare_admin"
    if any(k in t for k in ["meeting", "travel request", "okr", "office supplies"]):
        return "general_admin"
    if any(k in t for k in ["knowledge base", "documentation", "specification", "docs"]):
        return "knowledge_work"

    return default


def canonicalize_domain(
    domain: str | None,
    action: str | None,
    parameters: Dict[str, Any],
    raw_text: str,
) -> str:
    """
    Map model-friendly / fuzzy domains into the strict canonical domains
    used by the evaluation dataset.

    IMPORTANT:
    - We now ALWAYS let the text-based heuristics refine the domain, even if
      the model already chose a canonical domain. This recovers mis-classified
      retail / energy / healthcare / operations, etc.
    """

    d = _norm(domain)
    a = _norm(action)
    text = raw_text.lower()

    # -------------------------------
    # 1. Straight synonyms / casing
    # -------------------------------

    if d in {"it-ops", "it_ops", "it"}:
        return "it_ops"

    if d in {"software_testing"}:
        return "devops"

    if d in {"inventory_management"}:
        return "retail"

    if d in {"energy_management", "energy_management_additional"}:
        return "energy"

    if d in {"customer_analysis", "customer_analytics"}:
        if "ticket" in text or "sentiment" in text:
            return "customer_support"
        if "churn" in text or "retention" in text:
            return "analytics"
        return "analytics"

    if d == "customer_feedback":
        return "retail"

    if d == "contract_management":
        if a in ("approve_contract_renewal",) or "vendor_name" in parameters:
            return "procurement"
        return "legal"

    if d == "compliance":
        return "legal"

    if d == "audit":
        return "legal"

    if d in {"travel", "calendar", "communication", "management"}:
        return "general_admin"

    if d == "lab_management":
        return "healthcare_admin"

    if d in {"knowledge_management", "document_management", "documentation"}:
        return "knowledge_work"

    # ---------------------------------------------
    # 2. If domain is already canonical → still allow heuristics
    # ---------------------------------------------
    if d in _CANONICAL_DOMAINS:
        guessed = _heuristic_domain_from_text(text, default=d)
        return guessed or d

    # -------------------------------------------------
    # 3. Generic / missing / unknown domain → heuristics
    # -------------------------------------------------
    generic_markers = {"", "general", "misc", "unassigned", "other"}
    if d in generic_markers or domain is None:
        guessed = _heuristic_domain_from_text(text, default="general_admin")
        if guessed:
            return guessed
        return "general_admin"

    # If we reach here, we have some unknown string; try heuristics as best effort.
    guessed = _heuristic_domain_from_text(text, default=None)
    if guessed:
        return guessed

    # Default: return as-is (upper layer / registry will still enforce)
    return d or "general_admin"


def canonicalize_action(
    domain: str,
    action: str | None,
    parameters: Dict[str, Any],
    raw_text: str,
) -> str:
    """
    Map fuzzy / generic actions into strict canonical actions from the eval.
    """

    d = domain  # already canonical
    a = _norm(action)
    text = raw_text.lower()

    # --- Logistics ---------------------------------------------------------
    if d == "logistics":
        if a in {"book_truck", "book_transport", "create_truck_booking"}:
            return "book_truck"

        if a in {"list_vessels", "list_ships"}:
            return "list_vessels"

        if a in {"allocate_warehouse_slot", "allocate_slot"}:
            return "allocate_warehouse_slot"

        if a in {"list_delayed_shipments", "list_delays"}:
            return "list_delayed_shipments"

        if a in {"create_delivery_schedule", "create_schedule"}:
            return "create_delivery_schedule"

    # --- Finance -----------------------------------------------------------
    if d == "finance":
        if a in {"generate_cashflow_report", "cashflow_report"}:
            return "generate_cashflow_report"

        if a in {"list_overdue_invoices", "overdue_invoices"}:
            return "list_overdue_invoices"

        if a in {"show_operating_expenses", "operating_expenses"}:
            return "show_operating_expenses"

        if a in {"generate_tax_summary", "tax_summary"}:
            return "generate_tax_summary"

        if a in {"invoice_aging", "invoice_aging_report"}:
            return "invoice_aging"

        if a in {"prepare_budget_forecast", "budget_forecast"}:
            return "prepare_budget_forecast"

    # --- HR ---------------------------------------------------------------
    if d == "hr":
        if a in {"create_employee", "add_employee"}:
            return "create_employee"

        if a in {"list_vacations", "list_leaves"}:
            return "list_vacations"

        if a in {"add_leave", "create_leave"}:
            return "add_leave"

        if a in {"promote_employee", "promotion"}:
            return "promote_employee"

        if a in {"schedule_onboarding", "onboarding"}:
            return "schedule_onboarding"

    # --- IT Ops ------------------------------------------------------------
    if d == "it_ops":
        if a in {"create_ticket", "open_ticket", "open_incident"}:
            return "create_ticket"

        if a in {"restart_service", "restart"}:
            return "restart_service"

        if a in {"run_diagnostics", "diagnostics"}:
            return "run_diagnostics"

        if a in {"rotate_logs", "log_rotation"}:
            return "rotate_logs"

        if a in {"schedule_patch", "patch_update"}:
            return "schedule_patch"

        if a in {"draft_dr_plan", "disaster_recovery_plan"}:
            return "draft_dr_plan"

        if a in {"deploy_service", "deploy"}:
            return "deploy_service"

        if a in {"list_unresolved_tickets"}:
            return "list_unresolved_tickets"

        if a in {"list_outages"} and "outage" in text:
            return "list_outages"

    # --- DevOps ------------------------------------------------------------
    if d == "devops":
        if a in {"deploy_microservice", "deploy_service", "deploy"}:
            return "deploy_microservice"

        if a in {"rollback_service", "rollback"}:
            return "rollback_service"

        if a in {"adjust_resources", "scale_resources"}:
            return "adjust_resources"

        if a in {"rebuild_dashboard", "rebuild"}:
            return "rebuild_dashboard"

        if a in {"run_load_test", "load_test"}:
            return "run_load_test"

    # --- Customer Support --------------------------------------------------
    if d == "customer_support":
        if a == "list_tickets":
            return "list_tickets"

        if a == "list_unresolved_tickets":
            return "list_unresolved_tickets"

        if a in {"sentiment_classification", "classify_tickets"}:
            if "sentiment" in text or "emotion" in text:
                return "sentiment_classification"

        if a in {"list_escalations", "escalations"}:
            return "list_escalations"

        if a in {"create_case", "open_case"}:
            return "create_case"

        if a in {"escalate_ticket", "escalate"}:
            return "escalate_ticket"

    # --- Operations --------------------------------------------------------
    if d == "operations":
        if a == "create_checklist":
            return "create_checklist"

        if a in {"schedule_preventive_maintenance", "schedule_maintenance"}:
            return "schedule_maintenance"

        if a == "list_risks":
            return "list_risks"

        if a == "summarize_incidents":
            return "summarize_incidents"

        if a == "forecast_staffing":
            return "forecast_staffing"

        if a == "create_safety_checklist":
            return "create_safety_checklist"

    # --- Manufacturing -----------------------------------------------------
    if d == "manufacturing":
        # NEW: utilization mapping for CMD-089 type commands
        if a in {"machine_utilization", "show"} and "utilization" in text:
            return "machine_utilization"

        if a in {"machine_downtime_report", "downtime_report"}:
            return "machine_downtime_report"

        if a in {"optimize_process", "optimize_line_sequence"}:
            return "optimize_line_sequence"

        if a == "assign_technicians":
            return "assign_technicians"

        if a == "record_inspection_results":
            return "record_inspection_results"

        if a in {"schedule_calibration", "schedule_task"}:
            return "schedule_calibration"

        if a == "list_work_orders":
            return "list_work_orders"

    # --- Procurement -------------------------------------------------------
    if d == "procurement":
        if a == "list_overdue_suppliers":
            return "list_overdue_suppliers"

        if a == "approve_vendor_contract":
            return "approve_vendor_contract"

        if a == "create_sourcing_plan":
            return "create_sourcing_plan"

        if a == "procurement_savings_report":
            return "procurement_savings_report"

        if a == "create_procurement_tracker":
            return "create_procurement_tracker"

        if a == "create_purchase_order":
            return "create_purchase_order"

        if a == "initiate_procurement":
            return "initiate_procurement"

    # --- Legal -------------------------------------------------------------
    if d == "legal":
        if a == "draft_nda":
            return "draft_nda"

        if a == "list_compliance_actions":
            return "list_compliance_actions"

        if a == "review_contract":
            return "review_contract"

        if a == "draft_employment_contract":
            return "draft_employment_contract"

        if a == "review_compliance_docs":
            return "review_compliance_docs"

        if a == "prepare_briefing":
            return "prepare_briefing"

        if a == "summarize_audit_findings":
            return "summarize_audit_findings"

    # --- Retail ------------------------------------------------------------
    if d == "retail":
        if a == "check_inventory":
            return "check_inventory"

        if a == "generate_sales_report":
            return "generate_sales_report"

        if a == "list_stockout_risk":
            return "list_stockout_risk"

        if a == "summarize_feedback":
            return "summarize_feedback"

        if a == "plan_replenishment":
            return "plan_replenishment"

        if a == "top_products":
            return "top_products"

    # --- Energy ------------------------------------------------------------
    if d == "energy":
        if a in {"consumption_summary", "generate_summary", "create"} and (
            "consumption" in text or "energy" in text
        ):
            return "consumption_summary"

        if a in {"forecast_grid_demand", "forecast_demand"}:
            return "forecast_grid_demand"

        if a in {"list_outages", "list_events"}:
            return "list_outages"

        if a in {"renewable_output_analysis", "analyze"} and "renewable" in text:
            return "renewable_output_analysis"

        if a in {"inspect_outage_reports"} or "anomaly_detection" in a:
            return "inspect_outage_reports"

        if a == "optimize_energy_usage":
            return "optimize_energy_usage"

    # --- Analytics ---------------------------------------------------------
    if d == "analytics":
        if a == "revenue_breakdown":
            return "revenue_breakdown"

        if a == "retention_analysis":
            return "retention_analysis"

        if a == "forecast_demand":
            return "forecast_demand"

        if a == "churn_analysis":
            return "churn_analysis"

    # --- Sales -------------------------------------------------------------
    if d == "sales":
        if a == "create_opportunity":
            return "create_opportunity"

        if a == "show_pipeline":
            return "show_pipeline"

        if a == "win_loss_analysis":
            return "win_loss_analysis"

        if a == "list_opportunities":
            return "list_opportunities"

        if a == "top_products":
            return "top_products"

    # --- Marketing ---------------------------------------------------------
    if d == "marketing":
        if a == "create_campaign":
            return "create_campaign"

        if a == "analyze_spend":
            return "analyze_spend"

        if a == "engagement_report":
            return "engagement_report"

        if a == "competitive_report":
            return "competitive_report"

    # --- Healthcare Admin --------------------------------------------------
    if d == "healthcare_admin":
        if a == "schedule_followup":
            return "schedule_followup"

        if a == "claims_summary":
            return "claims_summary"

        if a == "list_pending_labs":
            return "list_pending_labs"

    # --- General Admin -----------------------------------------------------
    if d == "general_admin":
        if a == "create_travel_request":
            return "create_travel_request"

        if a == "list_meetings":
            return "list_meetings"

        if a == "draft_announcement":
            return "draft_announcement"

        if a == "summarize_okrs":
            return "summarize_okrs"

        if a == "create_procurement_tracker":
            return "create_procurement_tracker"

    # --- Knowledge Work ----------------------------------------------------
    if d == "knowledge_work":
        if a == "create_documentation":
            return "create_documentation"

        if a == "tag_documents":
            return "tag_documents"

        if a == "summarize_document":
            return "summarize_document"

    # If nothing matched, return the normalized action string as-is.
    return a


def canonicalize(parsed: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """
    Top-level entrypoint:
    - takes the raw parsed dict from the LLM
    - normalizes domain & action into your strict canonical space
    - returns updated dict.
    """
    data = dict(parsed)  # shallow copy
    params = data.get("parameters") or {}

    dom = canonicalize_domain(
        domain=data.get("domain"),
        action=data.get("action"),
        parameters=params,
        raw_text=raw_text,
    )

    act = canonicalize_action(
        domain=dom,
        action=data.get("action"),
        parameters=params,
        raw_text=raw_text,
    )

    data["domain"] = dom
    data["action"] = act
    data.setdefault("raw_text", raw_text)

    return data
