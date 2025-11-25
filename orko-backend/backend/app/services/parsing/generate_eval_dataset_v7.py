# backend/app/services/parsing/generate_eval_dataset_v7.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


# Existing v2 dataset path (your current 100 commands)
BASE_EVAL_PATH = Path("backend/tests/eval/parser_eval_set.yml").resolve()

# New v7 dataset path (300 commands)
V7_EVAL_PATH = Path("backend/tests/eval/parser_eval_set_v7.yml").resolve()


def _load_base_commands() -> List[Dict[str, Any]]:
    if not BASE_EVAL_PATH.exists():
        raise FileNotFoundError(f"Base eval set not found at: {BASE_EVAL_PATH}")

    with BASE_EVAL_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    cmds = data.get("commands", [])
    if not isinstance(cmds, list):
        raise ValueError("parser_eval_set.yml must contain a 'commands' list.")

    return cmds


def _next_id_number(existing: List[Dict[str, Any]]) -> int:
    """
    Find the next CMD-XXX number to use.
    Assumes IDs are of the form 'CMD-001', 'CMD-100', etc.
    """
    max_id = 0
    for item in existing:
        raw_id = item.get("id", "")
        if isinstance(raw_id, str) and raw_id.startswith("CMD-"):
            try:
                num = int(raw_id.split("-")[1])
                if num > max_id:
                    max_id = num
            except Exception:
                continue
    return max_id + 1


def _make_item(
    id_num: int,
    command: str,
    domain: str,
    action: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "id": f"CMD-{id_num:03d}",
        "command": command,
        "expected": {
            "domain": domain,
            "action": action,
            "parameters": params or {},
        },
    }


def _generate_synthetic_items(start_id: int, target_total: int) -> List[Dict[str, Any]]:
    """
    Generate synthetic multi-industry commands to reach target_total.
    We keep them realistic, but programmatic (so you don't have to
    write 200 by hand).
    """
    items: List[Dict[str, Any]] = []
    current_id = start_id

    # How many new commands we need in total
    needed = max(0, target_total - (start_id - 1))

    # Helper to add items but stop when we hit needed
    def add(cmd: Dict[str, Any]):
        nonlocal current_id, needed
        if needed <= 0:
            return False
        cmd["id"] = f"CMD-{current_id:03d}"
        current_id += 1
        needed -= 1
        items.append(cmd)
        return needed > 0

    # ------------- TRADING -------------
    trading_specs = [
        ("Create corn hedge for Q1.", "trading", "create_hedging_plan",
         {"commodity": "corn", "period": "Q1"}),
        ("Show PnL for coffee futures in LATAM.", "trading", "show_pnl",
         {"commodity": "coffee", "region": "LATAM"}),
        ("Update basis for rapeseed oil FOB Rotterdam.", "trading", "update_price_basis",
         {"commodity": "rapeseed oil", "location": "FOB Rotterdam"}),
        ("Create FX hedge plan for EUR exposure.", "trading", "create_hedging_plan",
         {"instrument": "FX", "currency": "EUR"}),
        ("Generate position report for soybean complex.", "trading", "generate_report",
         {"book": "soybean complex"}),
    ]
    for text, dom, action, params in trading_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- LOGISTICS -------------
    logistics_specs = [
        ("List vessels arriving in Santos next 10 days.", "logistics", "list_vessels",
         {"port": "Santos", "window": "10 days"}),
        ("Book a container shipment from Shanghai to Hamburg.", "logistics", "book_truck",
         {"mode": "container", "origin": "Shanghai", "destination": "Hamburg"}),
        ("Show all delayed rail shipments to Warsaw.", "logistics", "list_delayed_shipments",
         {"mode": "rail", "destination": "Warsaw"}),
        ("Allocate warehouse slot for cold-chain cargo in Dubai.", "logistics", "allocate_warehouse_slot",
         {"temperature_control": True, "location": "Dubai"}),
        ("Generate daily dispatch report for Mersin warehouse.", "logistics", "generate_report",
         {"warehouse": "Mersin", "period": "daily"}),
    ]
    for text, dom, action, params in logistics_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- FINANCE -------------
    finance_specs = [
        ("Generate monthly cashflow report for APAC.", "finance", "generate_cashflow_report",
         {"region": "APAC", "period": "monthly"}),
        ("Show invoice aging for retail customers.", "finance", "invoice_aging",
         {"segment": "retail"}),
        ("Generate PnL summary for global trading desk.", "finance", "generate_report",
         {"desk": "global trading", "metric": "PnL"}),
        ("List overdue invoices above 100k USD.", "finance", "list_overdue_invoices",
         {"min_amount": 100000}),
        ("Generate annual tax summary for 2023.", "finance", "generate_tax_summary",
         {"year": 2023}),
    ]
    for text, dom, action, params in finance_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- HR -------------
    hr_specs = [
        ("Create new employee record in London office.", "hr", "create_employee",
         {"location": "London"}),
        ("List employees whose probation ends this month.", "hr", "list_employees",
         {"filter": "probation_end_this_month"}),
        ("Schedule onboarding for 3 junior analysts.", "hr", "schedule_onboarding",
         {"role": "junior analyst", "count": 3}),
        ("Generate headcount report by department.", "hr", "generate_report",
         {"metric": "headcount", "group_by": "department"}),
        ("Promote Maria to Senior Product Manager.", "hr", "promote_employee",
         {"employee": "Maria", "role": "Senior Product Manager"}),
    ]
    for text, dom, action, params in hr_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- IT OPS -------------
    itops_specs = [
        ("Restart reporting API in EU cluster.", "it_ops", "restart_service",
         {"service": "reporting API", "cluster": "EU"}),
        ("Run diagnostics on Redis cache cluster.", "it_ops", "run_diagnostics",
         {"service": "redis-cache"}),
        ("Schedule patch update for fraud engine.", "it_ops", "schedule_patch",
         {"system": "fraud engine"}),
        ("Draft DR plan for core settlement system.", "it_ops", "draft_dr_plan",
         {"system": "core settlement"}),
        ("Check status of production Kubernetes cluster.", "it_ops", "check",
         {"environment": "production", "target": "kubernetes cluster"}),
    ]
    for text, dom, action, params in itops_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- DEVOPS -------------
    devops_specs = [
        ("Deploy analytics microservice to canary environment.", "devops", "deploy_microservice",
         {"service": "analytics", "environment": "canary"}),
        ("Rollback payments microservice to previous version.", "devops", "rollback_service",
         {"service": "payments"}),
        ("Run load test on checkout API with 10k users.", "devops", "run_load_test",
         {"api": "checkout", "users": 10000}),
        ("Rebuild observability dashboard for SRE team.", "devops", "rebuild_dashboard",
         {"audience": "SRE"}),
        ("Rotate secrets for CI/CD pipeline.", "devops", "rotate",
         {"target": "ci/cd pipeline secrets"}),
    ]
    for text, dom, action, params in devops_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- CUSTOMER SUPPORT -------------
    cs_specs = [
        ("Create a new support case for ACME Logistics.", "customer_support", "create_case",
         {"customer": "ACME Logistics"}),
        ("List unresolved tickets older than 72 hours.", "customer_support", "list_unresolved_tickets",
         {"age": "72h"}),
        ("Escalate ticket about failed onboarding emails.", "customer_support", "escalate_ticket",
         {"issue": "onboarding emails failed"}),
        ("Classify all open tickets by sentiment.", "customer_support", "sentiment_classification",
         {"scope": "open_tickets"}),
        ("List all customer escalations for premium accounts.", "customer_support", "list_escalations",
         {"segment": "premium"}),
    ]
    for text, dom, action, params in cs_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- OPERATIONS -------------
    ops_specs = [
        ("Create daily safety checklist for loading bay.", "operations", "create_checklist",
         {"area": "loading bay"}),
        ("Schedule maintenance for conveyor belt C3.", "operations", "schedule_maintenance",
         {"machine": "conveyor C3"}),
        ("List all open operational risks for APAC.", "operations", "list_risks",
         {"region": "APAC"}),
        ("Summarize incidents for global operations this week.", "operations", "summarize_incidents",
         {"period": "this week"}),
        ("Forecast staffing levels for night shift.", "operations", "forecast_staffing",
         {"shift": "night"}),
    ]
    for text, dom, action, params in ops_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- ANALYTICS -------------
    analytics_specs = [
        ("Generate revenue breakdown by product family.", "analytics", "revenue_breakdown",
         {"dimension": "product_family"}),
        ("Run churn analysis for SMB segment.", "analytics", "churn_analysis",
         {"segment": "SMB"}),
        ("Forecast demand for next 12 months in EMEA.", "analytics", "forecast_demand",
         {"horizon": "12 months", "region": "EMEA"}),
        ("Generate retention analysis for loyalty program.", "analytics", "retention_analysis",
         {"program": "loyalty"}),
        ("Summarize marketing attribution impact for Q4.", "analytics", "summarize",
         {"topic": "marketing attribution", "quarter": "Q4"}),
    ]
    for text, dom, action, params in analytics_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- SALES -------------
    sales_specs = [
        ("Create opportunity for MegaCorp renewal in Q2.", "sales", "create_opportunity",
         {"customer": "MegaCorp", "quarter": "Q2"}),
        ("Show sales pipeline for EMEA enterprise deals.", "sales", "show_pipeline",
         {"region": "EMEA", "segment": "enterprise"}),
        ("Generate win-loss analysis for mid-market deals.", "sales", "win_loss_analysis",
         {"segment": "mid-market"}),
        ("List opportunities closing in next 60 days.", "sales", "list_opportunities",
         {"close_window": "60 days"}),
        ("Generate sales forecast for North America.", "sales", "generate_forecast",
         {"region": "North America"}),
    ]
    for text, dom, action, params in sales_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- MARKETING -------------
    marketing_specs = [
        ("Create launch campaign for new smartwatch.", "marketing", "create_campaign",
         {"product": "smartwatch"}),
        ("Analyze marketing spend for digital channels in Q3.", "marketing", "analyze_spend",
         {"quarter": "Q3", "channel": "digital"}),
        ("Generate weekly engagement report for LinkedIn.", "marketing", "engagement_report",
         {"channel": "LinkedIn", "period": "weekly"}),
        ("Create competitive report for ESG-focused funds.", "marketing", "competitive_report",
         {"segment": "ESG funds"}),
        ("Summarize performance of email campaigns in August.", "marketing", "summarize",
         {"channel": "email", "month": "August"}),
    ]
    for text, dom, action, params in marketing_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- PROCUREMENT -------------
    procurement_specs = [
        ("Create purchase order for 1,000 office chairs.", "procurement", "create_purchase_order",
         {"item": "office chairs", "quantity": 1000}),
        ("List suppliers with overdue quality audits.", "procurement", "list_overdue_suppliers",
         {"filter": "quality_audit_overdue"}),
        ("Approve vendor contract extension for Nimbus Corp.", "procurement", "approve_vendor_contract",
         {"vendor": "Nimbus Corp"}),
        ("Create sourcing plan for cloud providers.", "procurement", "create_sourcing_plan",
         {"category": "cloud infrastructure"}),
        ("Generate weekly procurement savings report.", "procurement", "procurement_savings_report",
         {"period": "weekly"}),
    ]
    for text, dom, action, params in procurement_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- MANUFACTURING -------------
    mfg_specs = [
        ("Show machine downtime report for line A.", "manufacturing", "machine_downtime_report",
         {"line": "A"}),
        ("List open work orders in finishing section.", "manufacturing", "list_work_orders",
         {"section": "finishing"}),
        ("Schedule calibration for packaging line sensors.", "manufacturing", "schedule_calibration",
         {"equipment": "packaging sensors"}),
        ("Optimize line sequence for plant C bottling line.", "manufacturing", "optimize_line_sequence",
         {"line": "plant C bottling"}),
        ("Record inspection results for batch ZX-404.", "manufacturing", "record_inspection_results",
         {"batch": "ZX-404"}),
    ]
    for text, dom, action, params in mfg_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- LEGAL -------------
    legal_specs = [
        ("Draft NDA for potential JV discussions.", "legal", "draft_nda",
         {"purpose": "JV discussions"}),
        ("Review master service agreement for termination clause.", "legal", "review_contract",
         {"contract_type": "MSA"}),
        ("List open compliance actions for GDPR.", "legal", "list_compliance_actions",
         {"regulation": "GDPR"}),
        ("Prepare briefing for new AI regulation.", "legal", "prepare_briefing",
         {"regulation": "AI"}),
        ("Summarize audit findings for SOX controls.", "legal", "summarize_audit_findings",
         {"topic": "SOX controls"}),
    ]
    for text, dom, action, params in legal_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- RETAIL -------------
    retail_specs = [
        ("Check inventory for wireless earbuds in US stores.", "retail", "check_inventory",
         {"product": "wireless earbuds", "region": "US"}),
        ("List items with stockout risk above 80%.", "retail", "list_stockout_risk",
         {"threshold": 0.8}),
        ("Generate daily sales report for Istanbul flagship store.", "retail", "generate_sales_report",
         {"location": "Istanbul flagship", "period": "daily"}),
        ("Show top products for Black Friday campaign.", "retail", "top_products",
         {"event": "Black Friday"}),
        ("Plan replenishment for fast-moving SKUs.", "retail", "plan_replenishment",
         {"priority": "fast-moving"}),
    ]
    for text, dom, action, params in retail_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- ENERGY -------------
    energy_specs = [
        ("Generate monthly consumption summary for data center A.", "energy", "consumption_summary",
         {"site": "data center A", "period": "monthly"}),
        ("Forecast grid demand for Berlin region next week.", "energy", "forecast_grid_demand",
         {"region": "Berlin", "horizon": "next week"}),
        ("List outages longer than 4 hours in Q1.", "energy", "list_outages",
         {"duration": "4h", "quarter": "Q1"}),
        ("Optimize energy usage for HQ building.", "energy", "optimize_energy_usage",
         {"target": "HQ building"}),
        ("Analyze renewable output for solar farms in Spain.", "energy", "renewable_output_analysis",
         {"region": "Spain"}),
    ]
    for text, dom, action, params in energy_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- HEALTHCARE ADMIN -------------
    hc_specs = [
        ("Schedule follow-up visit for patient B203 next month.", "healthcare_admin", "schedule_followup",
         {"patient_id": "B203", "timeframe": "next month"}),
        ("List pending lab results older than 96 hours.", "healthcare_admin", "list_pending_labs",
         {"age": "96h"}),
        ("Generate monthly claims summary for provider group X.", "healthcare_admin", "claims_summary",
         {"period": "monthly", "provider_group": "X"}),
        ("Show appointment schedule for Dr. Smith today.", "healthcare_admin", "show",
         {"doctor": "Dr. Smith", "period": "today"}),
        ("Record insurance pre-authorization for procedure 784C.", "healthcare_admin", "record",
         {"procedure_code": "784C"}),
    ]
    for text, dom, action, params in hc_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- GENERAL ADMIN -------------
    ga_specs = [
        ("Create travel request for conference in Berlin next month.", "general_admin", "create_travel_request",
         {"destination": "Berlin", "time": "next month"}),
        ("List all meetings for leadership team tomorrow.", "general_admin", "list_meetings",
         {"period": "tomorrow", "audience": "leadership"}),
        ("Draft announcement for office relocation.", "general_admin", "draft_announcement",
         {"topic": "office relocation"}),
        ("Summarize OKRs for customer success team.", "general_admin", "summarize_okrs",
         {"team": "customer success"}),
        ("Create procurement tracker for remote work equipment.", "general_admin", "create_procurement_tracker",
         {"type": "remote work equipment"}),
    ]
    for text, dom, action, params in ga_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    # ------------- KNOWLEDGE WORK -------------
    kw_specs = [
        ("Create onboarding documentation for data platform.", "knowledge_work", "create_documentation",
         {"subject": "data platform onboarding"}),
        ("Tag documents related to climate risk.", "knowledge_work", "tag_documents",
         {"topic": "climate risk"}),
        ("Summarize product requirements document for design team.", "knowledge_work", "summarize_document",
         {"target_team": "design"}),
        ("Classify internal memos by topic.", "knowledge_work", "classify",
         {"scope": "internal memos"}),
        ("Generate summary of technical RFCs created this month.", "knowledge_work", "summarize",
         {"topic": "RFCs", "period": "this month"}),
    ]
    for text, dom, action, params in kw_specs:
        if not add(_make_item(0, text, dom, action, params)):
            return items

    return items


def main(target_total: int = 300) -> None:
    base_commands = _load_base_commands()
    start_id = _next_id_number(base_commands)

    synthetic_items = _generate_synthetic_items(start_id=start_id, target_total=target_total)

    all_commands = base_commands + synthetic_items

    data = {"commands": all_commands}

    V7_EVAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with V7_EVAL_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    print(f"Base commands:   {len(base_commands)}")
    print(f"Synthetic added: {len(synthetic_items)}")
    print(f"Total commands:  {len(all_commands)}")
    print(f"Written to:      {V7_EVAL_PATH}")


if __name__ == "__main__":
    main()
