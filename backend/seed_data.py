"""
Seed dataset for a FICTIONAL organisation used purely for demonstration.

    Organisation : Meridian Financial Group  (FICTIONAL - not a real company)
    Industry     : Banking & Financial Services

The ENGINE is industry-agnostic. Everything specific to banking lives in this
one file, so the same product could analyse healthcare, retail, or
manufacturing by swapping this data only.

Activity factor legend (all 0..1, they are observable FACTS about the work):
    rep   = repetitiveness           (higher -> easier to automate)
    rule  = rule-based               (higher -> easier to automate)
    data  = data availability        (higher -> easier to automate)
    dcx   = decision complexity      (higher -> HARDER to automate)
    hint  = human interaction        (higher -> HARDER to automate)
"""

ORGANIZATION = {
    "name": "Meridian Financial Group",
    "industry": "Banking & Financial Services",
    "description": (
        "A FICTIONAL mid-size retail and corporate bank used to demonstrate the "
        "AI Workforce Transformation Analyzer. Any resemblance to a real "
        "institution is coincidental."
    ),
    "is_fictional": 1,
}

# --- Skill catalogue ---------------------------------------------------------
SKILLS = [
    ("Data entry", "Operational", "Manual keying of structured data"),
    ("Spreadsheet modeling", "Analytical", "Building models and calculations in spreadsheets"),
    ("Financial analysis", "Analytical", "Interpreting financial statements and metrics"),
    ("Regulatory knowledge", "Domain", "Understanding of banking regulation"),
    ("Communication", "Interpersonal", "Clear written and verbal communication"),
    ("Relationship management", "Interpersonal", "Building and maintaining client trust"),
    ("Negotiation", "Interpersonal", "Reaching agreement on terms"),
    ("Risk assessment", "Analytical", "Evaluating credit, market and operational risk"),
    ("SQL / data querying", "Technical", "Extracting data from databases"),
    ("Attention to detail", "Operational", "Accuracy in repetitive checks"),
    ("Customer empathy", "Interpersonal", "Understanding and responding to customer needs"),
    ("Document review", "Operational", "Reading and validating documents"),
    ("Judgment & decision-making", "Cognitive", "Weighing ambiguous trade-offs"),
    ("Scripting / automation", "Technical", "Automating tasks with code"),
    ("Statistical modeling", "Technical", "Building predictive/statistical models"),
    ("Fraud detection", "Domain", "Spotting anomalous or fraudulent patterns"),
    ("Product knowledge", "Domain", "Understanding of banking products"),
    ("Sales", "Interpersonal", "Persuading and closing"),
    ("Compliance monitoring", "Domain", "Checking activity against policy"),
    ("Reconciliation", "Operational", "Matching records across systems"),
    ("Stakeholder management", "Interpersonal", "Aligning internal partners"),
    ("Presentation", "Interpersonal", "Communicating findings to an audience"),
    ("Credit analysis", "Analytical", "Assessing borrower creditworthiness"),
    ("AML investigation", "Domain", "Investigating money-laundering risk"),
    ("Process design", "Cognitive", "Designing and improving workflows"),
    ("AI tool orchestration", "Emerging", "Directing and supervising AI systems"),
    ("Prompt & workflow design", "Emerging", "Designing effective AI prompts/workflows"),
    ("Data storytelling", "Emerging", "Turning analysis into a narrative for decisions"),
    ("Exception handling", "Cognitive", "Resolving cases that fall outside the rules"),
    ("Model validation", "Technical", "Independently checking model soundness"),
]

# --- AI capability catalogue -------------------------------------------------
AI_CAPABILITIES = [
    ("Document extraction (OCR/NLP)", "Perception", "Read and structure text from documents", 0.9),
    ("Anomaly / fraud detection (ML)", "Prediction", "Flag unusual patterns in transactions", 0.85),
    ("Robotic process automation (RPA)", "Automation", "Automate deterministic system steps", 0.9),
    ("Conversational AI (assistants)", "Interaction", "Handle routine conversations", 0.75),
    ("Predictive analytics / forecasting", "Prediction", "Forecast outcomes from history", 0.8),
    ("Generative drafting (LLM)", "Generation", "Draft documents, memos, and summaries", 0.8),
    ("Entity resolution / matching", "Reasoning", "Match and dedupe records across systems", 0.85),
    ("Recommendation engines", "Prediction", "Suggest next-best action or product", 0.75),
    ("Automated reconciliation", "Automation", "Match ledgers and flag breaks", 0.85),
    ("Speech-to-text / transcription", "Perception", "Transcribe and summarise calls", 0.85),
    ("Knowledge retrieval (RAG)", "Reasoning", "Answer questions over policy/knowledge bases", 0.75),
    ("Credit scoring models", "Prediction", "Score creditworthiness from data", 0.8),
]

# --- Research evidence (REAL published research; organisation is fictional) ---
RESEARCH = [
    ("World Economic Forum", "Future of Jobs Report 2023", "https://www.weforum.org/reports/the-future-of-jobs-report-2023", 2023, "automation",
     "Estimates that a large share of routine data-processing and clerical tasks are highly exposed to automation this decade."),
    ("McKinsey Global Institute", "The economic potential of generative AI", "https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/the-economic-potential-of-generative-ai-the-next-productivity-frontier", 2023, "augmentation",
     "Finds generative AI most often augments knowledge work by drafting and synthesising rather than fully replacing it."),
    ("OECD", "OECD Employment Outlook 2023: Artificial Intelligence and the Labour Market", "https://www.oecd.org/employment/outlook/", 2023, "reskilling",
     "Highlights that AI adoption raises demand for reskilling and for skills that complement AI."),
    ("IMF", "Gen-AI: Artificial Intelligence and the Future of Work", "https://www.imf.org/en/Publications/Staff-Discussion-Notes/Issues/2024/01/14/Gen-AI-Artificial-Intelligence-and-the-Future-of-Work-542379", 2024, "augmentation",
     "Notes that high-exposure jobs are often high-complementarity, meaning AI augments experienced professionals."),
    ("Bank for International Settlements", "The impact of AI on the banking workforce", "https://www.bis.org/", 2024, "automation",
     "Documents rapid adoption of automation in payments, reconciliation, and back-office banking operations."),
    ("World Economic Forum", "Future of Jobs Report 2023 - Human skills", "https://www.weforum.org/reports/the-future-of-jobs-report-2023", 2023, "human",
     "Identifies analytical thinking, relationship-building, and judgment as skills least exposed to automation."),
]


# ---------------------------------------------------------------------------
# Roles. Each activity tuple:
#   (name, time_share, rep, rule, data, dcx, hint, [skills], description)
# ---------------------------------------------------------------------------
ROLES = [
    #           #####================= RETAIL BANKING =================
    {
        "name": "Bank Teller", "department": "Retail Banking", "seniority": "Junior",
        "description": "Handles in-branch cash and deposit transactions for retail customers.",
        "processes": [
            {"name": "Counter Transaction Processing", "description": "Process day-to-day counter transactions.",
             "activities": [
                ("Process deposits and withdrawals", 1.0, 0.95, 0.95, 0.9, 0.15, 0.4,
                 ["Data entry", "Attention to detail", "Product knowledge"], "Key cash and cheque transactions into core banking."),
                ("Verify identity documents", 0.6, 0.8, 0.85, 0.8, 0.25, 0.5,
                 ["Document review", "Attention to detail"], "Check ID against records for transactions."),
             ]},
            {"name": "Customer Servicing", "description": "Front-desk customer help.",
             "activities": [
                ("Answer routine account queries", 0.8, 0.7, 0.6, 0.7, 0.3, 0.8,
                 ["Communication", "Customer empathy", "Product knowledge"], "Explain balances, fees, and simple products."),
                ("Refer complex needs to specialists", 0.4, 0.4, 0.5, 0.4, 0.6, 0.85,
                 ["Judgment & decision-making", "Relationship management"], "Identify and hand off complex cases."),
             ]},
        ],
    },
    {
        "name": "Personal Banker", "department": "Retail Banking", "seniority": "Mid",
        "description": "Advises retail customers on products and grows relationships.",
        "processes": [
            {"name": "Needs-based Advising", "description": "Match customers to products.",
             "activities": [
                ("Assess customer financial needs", 0.7, 0.3, 0.4, 0.5, 0.7, 0.85,
                 ["Relationship management", "Judgment & decision-making", "Product knowledge"], "Understand goals and recommend products."),
                ("Open and configure accounts", 0.5, 0.85, 0.9, 0.85, 0.25, 0.5,
                 ["Data entry", "Attention to detail"], "Set up accounts and products in systems."),
                ("Cross-sell relevant products", 0.5, 0.4, 0.4, 0.6, 0.5, 0.8,
                 ["Sales", "Communication", "Customer empathy"], "Offer suitable additional products."),
             ]},
        ],
    },
    {
        "name": "Branch Manager", "department": "Retail Banking", "seniority": "Senior",
        "description": "Runs a branch: people, targets, service quality, and local risk.",
        "processes": [
            {"name": "Branch Operations Management", "description": "Oversee branch performance.",
             "activities": [
                ("Coach and manage branch staff", 0.6, 0.2, 0.3, 0.4, 0.85, 0.9,
                 ["Stakeholder management", "Judgment & decision-making", "Communication"], "Develop and lead the team."),
                ("Review daily performance reports", 0.4, 0.7, 0.7, 0.85, 0.4, 0.4,
                 ["Financial analysis", "Data storytelling"], "Track KPIs and branch metrics."),
                ("Handle escalated customer issues", 0.4, 0.3, 0.4, 0.4, 0.75, 0.9,
                 ["Customer empathy", "Exception handling", "Negotiation"], "Resolve complaints and exceptions."),
             ]},
        ],
    },
    {
        "name": "Consumer Loan Officer", "department": "Retail Banking", "seniority": "Mid",
        "description": "Originates and processes consumer loan applications.",
        "processes": [
            {"name": "Loan Origination", "description": "Take applications through to decision.",
             "activities": [
                ("Collect and validate application data", 0.7, 0.85, 0.85, 0.85, 0.3, 0.5,
                 ["Document review", "Data entry", "Attention to detail"], "Gather and check applicant documents."),
                ("Run affordability and credit checks", 0.6, 0.8, 0.9, 0.9, 0.4, 0.3,
                 ["Credit analysis", "Risk assessment"], "Pull bureau data and score affordability."),
                ("Explain terms and close the loan", 0.5, 0.4, 0.5, 0.5, 0.55, 0.85,
                 ["Communication", "Sales", "Relationship management"], "Walk the customer through the offer."),
             ]},
        ],
    },
    {
        "name": "Mortgage Underwriter", "department": "Retail Banking", "seniority": "Senior",
        "description": "Assesses mortgage risk and makes lending decisions.",
        "processes": [
            {"name": "Mortgage Underwriting", "description": "Decision mortgage applications.",
             "activities": [
                ("Verify income and documents", 0.6, 0.85, 0.85, 0.85, 0.35, 0.35,
                 ["Document review", "Attention to detail"], "Validate payslips, statements, valuations."),
                ("Assess credit and collateral risk", 0.7, 0.55, 0.7, 0.8, 0.7, 0.3,
                 ["Credit analysis", "Risk assessment", "Judgment & decision-making"], "Evaluate the overall risk of the loan."),
                ("Make and document lending decision", 0.5, 0.35, 0.55, 0.6, 0.8, 0.45,
                 ["Judgment & decision-making", "Regulatory knowledge"], "Approve/decline with rationale."),
             ]},
        ],
    },
    {
        "name": "Collections Specialist", "department": "Retail Banking", "seniority": "Junior",
        "description": "Recovers overdue balances and arranges repayment plans.",
        "processes": [
            {"name": "Arrears Management", "description": "Work overdue accounts.",
             "activities": [
                ("Prioritise overdue accounts", 0.5, 0.8, 0.85, 0.9, 0.35, 0.2,
                 ["Data entry", "Risk assessment"], "Rank accounts by risk and value."),
                ("Contact customers for repayment", 0.7, 0.5, 0.5, 0.6, 0.5, 0.9,
                 ["Communication", "Negotiation", "Customer empathy"], "Call/write to arrange payment."),
                ("Negotiate repayment plans", 0.5, 0.35, 0.45, 0.5, 0.7, 0.9,
                 ["Negotiation", "Judgment & decision-making"], "Agree affordable plans."),
             ]},
        ],
    },
    # ================= OPERATIONS =================
    {
        "name": "Payments Operations Analyst", "department": "Operations", "seniority": "Mid",
        "description": "Processes and monitors domestic and cross-border payments.",
        "processes": [
            {"name": "Payment Processing", "description": "Execute and monitor payments.",
             "activities": [
                ("Process payment instructions", 0.8, 0.95, 0.95, 0.95, 0.15, 0.15,
                 ["Data entry", "Reconciliation", "Attention to detail"], "Release straight-through payments."),
                ("Investigate failed/returned payments", 0.6, 0.55, 0.6, 0.7, 0.6, 0.4,
                 ["Exception handling", "Judgment & decision-making"], "Resolve exceptions and repairs."),
             ]},
        ],
    },
    {
        "name": "Reconciliation Analyst", "department": "Operations", "seniority": "Junior",
        "description": "Matches internal ledgers with external statements.",
        "processes": [
            {"name": "Account Reconciliation", "description": "Match and resolve breaks.",
             "activities": [
                ("Match ledger to bank statements", 0.8, 0.95, 0.95, 0.95, 0.15, 0.1,
                 ["Reconciliation", "Attention to detail", "Data entry"], "Auto/manual matching of entries."),
                ("Investigate and clear breaks", 0.6, 0.6, 0.65, 0.75, 0.55, 0.35,
                 ["Exception handling", "Judgment & decision-making"], "Find root cause of mismatches."),
             ]},
        ],
    },
    {
        "name": "Trade Settlement Analyst", "department": "Operations", "seniority": "Mid",
        "description": "Ensures securities trades settle correctly and on time.",
        "processes": [
            {"name": "Trade Settlement", "description": "Confirm and settle trades.",
             "activities": [
                ("Confirm and match trades", 0.7, 0.9, 0.9, 0.9, 0.25, 0.2,
                 ["Reconciliation", "Attention to detail"], "Match trade details with counterparties."),
                ("Resolve settlement failures", 0.6, 0.55, 0.6, 0.7, 0.65, 0.5,
                 ["Exception handling", "Stakeholder management"], "Chase and fix failed settlements."),
             ]},
        ],
    },
    {
        "name": "KYC Analyst", "department": "Operations", "seniority": "Junior",
        "description": "Performs know-your-customer onboarding and reviews.",
        "processes": [
            {"name": "Customer Due Diligence", "description": "Verify and risk-rate customers.",
             "activities": [
                ("Collect and verify KYC documents", 0.8, 0.85, 0.85, 0.85, 0.3, 0.35,
                 ["Document review", "Data entry", "Attention to detail"], "Gather identity/ownership evidence."),
                ("Screen against sanctions/PEP lists", 0.6, 0.8, 0.9, 0.9, 0.4, 0.2,
                 ["Compliance monitoring", "Attention to detail"], "Run and clear screening hits."),
                ("Assess and document risk rating", 0.5, 0.4, 0.55, 0.6, 0.7, 0.35,
                 ["Risk assessment", "Judgment & decision-making"], "Decide customer risk level."),
             ]},
        ],
    },
    {
        "name": "Fraud Analyst", "department": "Operations", "seniority": "Mid",
        "description": "Detects and investigates fraudulent activity.",
        "processes": [
            {"name": "Fraud Monitoring", "description": "Monitor and investigate alerts.",
             "activities": [
                ("Triage transaction fraud alerts", 0.7, 0.7, 0.75, 0.9, 0.45, 0.2,
                 ["Fraud detection", "Attention to detail"], "Work model-generated alerts."),
                ("Investigate suspicious cases", 0.6, 0.4, 0.5, 0.7, 0.75, 0.5,
                 ["Fraud detection", "Judgment & decision-making", "Exception handling"], "Deep-dive complex fraud."),
             ]},
        ],
    },
    # ================= RISK & COMPLIANCE =================
    {
        "name": "Credit Risk Analyst", "department": "Risk & Compliance", "seniority": "Mid",
        "description": "Analyses portfolio credit risk and builds risk reporting.",
        "processes": [
            {"name": "Credit Risk Analysis", "description": "Measure and report credit risk.",
             "activities": [
                ("Extract and clean risk data", 0.6, 0.8, 0.8, 0.9, 0.35, 0.15,
                 ["SQL / data querying", "Data entry"], "Prepare data for risk models."),
                ("Run portfolio risk models", 0.6, 0.65, 0.7, 0.85, 0.6, 0.2,
                 ["Statistical modeling", "Risk assessment"], "Compute PD/LGD and exposures."),
                ("Interpret results for committee", 0.5, 0.3, 0.4, 0.5, 0.8, 0.7,
                 ["Data storytelling", "Judgment & decision-making", "Presentation"], "Explain risk to decision-makers."),
             ]},
        ],
    },
    {
        "name": "AML Compliance Officer", "department": "Risk & Compliance", "seniority": "Senior",
        "description": "Oversees anti-money-laundering controls and reporting.",
        "processes": [
            {"name": "AML Investigation", "description": "Investigate and report suspicious activity.",
             "activities": [
                ("Review transaction monitoring alerts", 0.7, 0.7, 0.75, 0.85, 0.5, 0.25,
                 ["AML investigation", "Compliance monitoring"], "Clear or escalate AML alerts."),
                ("Investigate and file SARs", 0.6, 0.35, 0.5, 0.6, 0.8, 0.5,
                 ["AML investigation", "Judgment & decision-making", "Regulatory knowledge"], "Build and file suspicious-activity reports."),
             ]},
        ],
    },
    {
        "name": "Regulatory Reporting Analyst", "department": "Risk & Compliance", "seniority": "Mid",
        "description": "Prepares mandatory regulatory returns.",
        "processes": [
            {"name": "Regulatory Reporting", "description": "Compile and submit returns.",
             "activities": [
                ("Aggregate data for returns", 0.7, 0.9, 0.9, 0.9, 0.3, 0.15,
                 ["SQL / data querying", "Reconciliation", "Attention to detail"], "Pull and combine reporting data."),
                ("Validate against regulatory rules", 0.6, 0.75, 0.85, 0.85, 0.5, 0.25,
                 ["Regulatory knowledge", "Compliance monitoring"], "Check figures against rules."),
                ("Sign off and submit returns", 0.4, 0.3, 0.5, 0.6, 0.75, 0.55,
                 ["Judgment & decision-making", "Regulatory knowledge"], "Review and approve submission."),
             ]},
        ],
    },
    {
        "name": "Model Risk Analyst", "department": "Risk & Compliance", "seniority": "Senior",
        "description": "Independently validates quantitative models.",
        "processes": [
            {"name": "Model Validation", "description": "Challenge and validate models.",
             "activities": [
                ("Reproduce and test model results", 0.6, 0.6, 0.65, 0.8, 0.6, 0.2,
                 ["Model validation", "Statistical modeling", "Scripting / automation"], "Independently re-run models."),
                ("Assess assumptions and limitations", 0.5, 0.25, 0.4, 0.5, 0.85, 0.5,
                 ["Judgment & decision-making", "Model validation"], "Critically challenge the model."),
             ]},
        ],
    },
    # ================= FINANCE =================
    {
        "name": "Finance Analyst (FP&A)", "department": "Finance", "seniority": "Mid",
        "description": "Owns budgeting, forecasting, and management reporting.",
        "processes": [
            {"name": "Planning & Forecasting", "description": "Build budgets and forecasts.",
             "activities": [
                ("Consolidate actuals from systems", 0.6, 0.9, 0.9, 0.9, 0.3, 0.15,
                 ["SQL / data querying", "Spreadsheet modeling", "Reconciliation"], "Gather and consolidate financials."),
                ("Build forecast models", 0.6, 0.6, 0.65, 0.8, 0.6, 0.25,
                 ["Spreadsheet modeling", "Financial analysis", "Statistical modeling"], "Model future performance."),
                ("Present insights to leadership", 0.5, 0.25, 0.35, 0.5, 0.8, 0.75,
                 ["Data storytelling", "Presentation", "Judgment & decision-making"], "Advise leaders on the numbers."),
             ]},
        ],
    },
    {
        "name": "Procurement Analyst", "department": "Finance", "seniority": "Mid",
        "description": "Manages sourcing, vendors, and purchasing.",
        "processes": [
            {"name": "Source-to-Contract", "description": "Source and contract suppliers.",
             "activities": [
                ("Process purchase requisitions", 0.7, 0.9, 0.9, 0.9, 0.25, 0.2,
                 ["Data entry", "Attention to detail"], "Turn requests into POs."),
                ("Analyse supplier quotes and spend", 0.6, 0.65, 0.7, 0.85, 0.55, 0.3,
                 ["Financial analysis", "Spreadsheet modeling"], "Compare bids and spend patterns."),
                ("Negotiate contracts with vendors", 0.5, 0.3, 0.4, 0.5, 0.75, 0.9,
                 ["Negotiation", "Relationship management", "Judgment & decision-making"], "Agree terms with suppliers."),
             ]},
        ],
    },
    {
        "name": "Accounts Payable Clerk", "department": "Finance", "seniority": "Junior",
        "description": "Processes supplier invoices and payments.",
        "processes": [
            {"name": "Invoice Processing", "description": "Process invoices to payment.",
             "activities": [
                ("Capture and code invoices", 0.8, 0.95, 0.95, 0.9, 0.15, 0.15,
                 ["Data entry", "Document review", "Attention to detail"], "Enter and code supplier invoices."),
                ("Match invoices to POs/receipts", 0.7, 0.95, 0.95, 0.95, 0.2, 0.1,
                 ["Reconciliation", "Attention to detail"], "Three-way match before payment."),
                ("Resolve invoice discrepancies", 0.4, 0.5, 0.55, 0.65, 0.55, 0.6,
                 ["Exception handling", "Communication"], "Chase and fix mismatches."),
             ]},
        ],
    },
    {
        "name": "Treasury Analyst", "department": "Finance", "seniority": "Mid",
        "description": "Manages liquidity, cash, and funding.",
        "processes": [
            {"name": "Liquidity Management", "description": "Manage daily cash and funding.",
             "activities": [
                ("Produce daily cash position", 0.6, 0.9, 0.9, 0.9, 0.3, 0.15,
                 ["Spreadsheet modeling", "Reconciliation"], "Consolidate the cash position."),
                ("Forecast short-term liquidity", 0.5, 0.6, 0.65, 0.8, 0.6, 0.25,
                 ["Statistical modeling", "Financial analysis"], "Project inflows/outflows."),
                ("Decide funding actions", 0.4, 0.3, 0.45, 0.55, 0.8, 0.6,
                 ["Judgment & decision-making", "Risk assessment"], "Choose funding/investment moves."),
             ]},
        ],
    },
    # ================= CORPORATE & WEALTH =================
    {
        "name": "Corporate Relationship Manager", "department": "Corporate Banking", "seniority": "Senior",
        "description": "Owns corporate client relationships and deal origination.",
        "processes": [
            {"name": "Client Relationship Management", "description": "Grow corporate relationships.",
             "activities": [
                ("Prepare client review packs", 0.5, 0.7, 0.7, 0.8, 0.45, 0.35,
                 ["Spreadsheet modeling", "Data storytelling"], "Assemble data-heavy review materials."),
                ("Advise clients on solutions", 0.7, 0.2, 0.3, 0.45, 0.85, 0.95,
                 ["Relationship management", "Judgment & decision-making", "Product knowledge"], "Consult on complex needs."),
                ("Negotiate and structure deals", 0.6, 0.25, 0.4, 0.5, 0.85, 0.9,
                 ["Negotiation", "Financial analysis", "Judgment & decision-making"], "Structure bespoke financing."),
             ]},
        ],
    },
    {
        "name": "Investment Research Analyst", "department": "Corporate Banking", "seniority": "Mid",
        "description": "Produces research and valuations on sectors and companies.",
        "processes": [
            {"name": "Equity/Credit Research", "description": "Research and publish views.",
             "activities": [
                ("Gather market and company data", 0.6, 0.85, 0.85, 0.9, 0.3, 0.15,
                 ["SQL / data querying", "Financial analysis"], "Collect fundamentals and market data."),
                ("Build valuation models", 0.6, 0.6, 0.65, 0.8, 0.65, 0.2,
                 ["Spreadsheet modeling", "Financial analysis", "Statistical modeling"], "Model company/sector value."),
                ("Write and defend research views", 0.6, 0.25, 0.4, 0.5, 0.8, 0.7,
                 ["Data storytelling", "Judgment & decision-making", "Presentation"], "Form and communicate a thesis."),
             ]},
        ],
    },
    {
        "name": "Wealth Advisor", "department": "Wealth Management", "seniority": "Senior",
        "description": "Advises high-net-worth clients on investments and planning.",
        "processes": [
            {"name": "Wealth Advisory", "description": "Plan and manage client wealth.",
             "activities": [
                ("Generate portfolio proposals", 0.5, 0.6, 0.7, 0.85, 0.5, 0.3,
                 ["Financial analysis", "Product knowledge"], "Draft allocation proposals."),
                ("Understand client goals and risk", 0.7, 0.25, 0.35, 0.5, 0.8, 0.95,
                 ["Relationship management", "Customer empathy", "Judgment & decision-making"], "Deeply understand the client."),
                ("Review and rebalance portfolios", 0.5, 0.55, 0.65, 0.8, 0.6, 0.5,
                 ["Financial analysis", "Risk assessment"], "Keep portfolios aligned to goals."),
             ]},
        ],
    },
    # ================= TECHNOLOGY & SERVICE =================
    {
        "name": "Data Analyst", "department": "Data & Analytics", "seniority": "Mid",
        "description": "Turns raw data into decisions across the bank.",
        "processes": [
            {"name": "Analytics Delivery", "description": "Deliver analysis and dashboards.",
             "activities": [
                ("Extract and transform data", 0.7, 0.85, 0.85, 0.9, 0.35, 0.15,
                 ["SQL / data querying", "Scripting / automation"], "Build data pipelines/queries."),
                ("Build dashboards and reports", 0.6, 0.7, 0.75, 0.85, 0.4, 0.2,
                 ["Data storytelling", "Spreadsheet modeling"], "Create reusable reporting."),
                ("Advise stakeholders on findings", 0.5, 0.3, 0.4, 0.5, 0.75, 0.75,
                 ["Data storytelling", "Stakeholder management", "Judgment & decision-making"], "Translate data into action."),
             ]},
        ],
    },
    {
        "name": "Contact Center Representative", "department": "Customer Service", "seniority": "Junior",
        "description": "Handles inbound customer calls and messages.",
        "processes": [
            {"name": "Customer Support", "description": "Resolve customer contacts.",
             "activities": [
                ("Answer routine customer requests", 0.8, 0.75, 0.7, 0.8, 0.3, 0.85,
                 ["Communication", "Customer empathy", "Product knowledge"], "Handle common queries."),
                ("Log and categorise contacts", 0.6, 0.9, 0.9, 0.9, 0.2, 0.3,
                 ["Data entry", "Attention to detail"], "Record contact details in CRM."),
                ("Resolve complex complaints", 0.4, 0.35, 0.45, 0.5, 0.7, 0.9,
                 ["Exception handling", "Negotiation", "Customer empathy"], "De-escalate and resolve issues."),
             ]},
        ],
    },
    {
        "name": "IT Support Analyst", "department": "Technology", "seniority": "Junior",
        "description": "Provides first/second-line technology support.",
        "processes": [
            {"name": "IT Service Desk", "description": "Resolve technology incidents.",
             "activities": [
                ("Triage and route tickets", 0.7, 0.85, 0.8, 0.9, 0.3, 0.4,
                 ["Data entry", "Attention to detail"], "Classify and assign incidents."),
                ("Resolve common technical issues", 0.6, 0.7, 0.7, 0.8, 0.45, 0.55,
                 ["Scripting / automation", "Communication"], "Fix known/repeatable problems."),
                ("Diagnose novel incidents", 0.4, 0.3, 0.4, 0.5, 0.75, 0.6,
                 ["Judgment & decision-making", "Exception handling"], "Investigate new problems."),
             ]},
        ],
    },
]
