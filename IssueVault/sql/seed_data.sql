-- ResolveHub seed data
-- Password for all seeded users: Password@123
-- Hash format: sha256$issuevaultseed$<digest>

PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO roles (role_name, description) VALUES ('end_user', 'Can submit and track own issues');
INSERT OR IGNORE INTO roles (role_name, description) VALUES ('support_analyst', 'Can triage and update assigned issues');
INSERT OR IGNORE INTO roles (role_name, description) VALUES ('consultant', 'Can investigate and resolve issues');
INSERT OR IGNORE INTO roles (role_name, description) VALUES ('manager', 'Can view dashboards and reports');
INSERT OR IGNORE INTO roles (role_name, description) VALUES ('admin', 'Can manage users and settings');

INSERT OR IGNORE INTO teams (team_name, description) VALUES ('Customer Support', 'Frontline support');
INSERT OR IGNORE INTO teams (team_name, description) VALUES ('Platform Engineering', 'Backend and infra');
INSERT OR IGNORE INTO teams (team_name, description) VALUES ('Consulting', 'Investigation and resolution');
INSERT OR IGNORE INTO teams (team_name, description) VALUES ('Management', 'Operational oversight');

INSERT OR IGNORE INTO issue_categories (category_name, description, is_active) VALUES ('Application Bug', 'Defect in app behavior', 'Y');
INSERT OR IGNORE INTO issue_categories (category_name, description, is_active) VALUES ('Database', 'Data model and SQL runtime', 'Y');
INSERT OR IGNORE INTO issue_categories (category_name, description, is_active) VALUES ('Integration', 'External systems and APIs', 'Y');
INSERT OR IGNORE INTO issue_categories (category_name, description, is_active) VALUES ('Infrastructure', 'Runtime and hosting', 'Y');
INSERT OR IGNORE INTO issue_categories (category_name, description, is_active) VALUES ('Data Quality', 'Incorrect or inconsistent data', 'Y');
INSERT OR IGNORE INTO issue_categories (category_name, description, is_active) VALUES ('Configuration', 'Config and environment issue', 'Y');

INSERT OR IGNORE INTO issue_tags (tag_name) VALUES ('urgent');
INSERT OR IGNORE INTO issue_tags (tag_name) VALUES ('customer-facing');
INSERT OR IGNORE INTO issue_tags (tag_name) VALUES ('release-blocker');
INSERT OR IGNORE INTO issue_tags (tag_name) VALUES ('billing');
INSERT OR IGNORE INTO issue_tags (tag_name) VALUES ('api');

INSERT OR IGNORE INTO releases (release_name, release_date, notes) VALUES ('2026.1', '2026-01-15', 'Quarterly release');
INSERT OR IGNORE INTO releases (release_name, release_date, notes) VALUES ('2026.2', '2026-03-31', 'Stability release');

INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role_id, team_id, is_active)
VALUES ('end_user_1', 'Emma Reed', 'emma.reed@resolvehub.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'end_user'),
        (SELECT team_id FROM teams WHERE team_name = 'Customer Support'),
        'Y');

INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role_id, team_id, is_active)
VALUES ('end_user_2', 'Noah James', 'noah.james@resolvehub.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'end_user'),
        (SELECT team_id FROM teams WHERE team_name = 'Customer Support'),
        'Y');

INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role_id, team_id, is_active)
VALUES ('support_1', 'Ava Singh', 'ava.singh@resolvehub.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'support_analyst'),
        (SELECT team_id FROM teams WHERE team_name = 'Customer Support'),
        'Y');

INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role_id, team_id, is_active)
VALUES ('support_2', 'Liam Park', 'liam.park@resolvehub.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'support_analyst'),
        (SELECT team_id FROM teams WHERE team_name = 'Customer Support'),
        'Y');

INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role_id, team_id, is_active)
VALUES ('consultant_1', 'Mia Thompson', 'mia.thompson@resolvehub.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'consultant'),
        (SELECT team_id FROM teams WHERE team_name = 'Consulting'),
        'Y');

INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role_id, team_id, is_active)
VALUES ('consultant_2', 'Ethan Alvarez', 'ethan.alvarez@resolvehub.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'consultant'),
        (SELECT team_id FROM teams WHERE team_name = 'Consulting'),
        'Y');

INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role_id, team_id, is_active)
VALUES ('manager_1', 'Sophia Clarke', 'sophia.clarke@resolvehub.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'manager'),
        (SELECT team_id FROM teams WHERE team_name = 'Management'),
        'Y');

INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role_id, team_id, is_active)
VALUES ('admin_1', 'Oliver Brooks', 'oliver.brooks@resolvehub.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'admin'),
        (SELECT team_id FROM teams WHERE team_name = 'Management'),
        'Y');

INSERT OR IGNORE INTO issues (
    issue_id, title, description, module_name, environment, severity, priority, status, category_id, error_code,
    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at, updated_at
)
VALUES
(1, 'Invoice posting fails with ORA-20001',
    'Posting fails when tax adjustments are applied during close.',
    'Billing', 'Production', 'Critical', 'P1', 'Resolved',
    (SELECT category_id FROM issue_categories WHERE category_name='Database'),
    'ORA-20001',
    'Open invoice and submit posting with tax adjustment.',
    'Invoice should post.', 'Rollback with ORA-20001.', 'Month-end close blocked.',
    (SELECT user_id FROM users WHERE username='end_user_1'),
    (SELECT user_id FROM users WHERE username='consultant_1'),
    (SELECT release_id FROM releases WHERE release_name='2026.1'),
    datetime('now', '-10 days'), datetime('now', '-7 days')
),
(2, 'Login redirect loop after SSO timeout',
    'User redirects repeatedly between login and callback.',
    'Authentication', 'Production', 'High', 'P1', 'In Progress',
    (SELECT category_id FROM issue_categories WHERE category_name='Integration'),
    'AUTH-LOOP-17',
    'Expire session then open protected URL.',
    'Single redirect and return.', 'Infinite redirect loop.', 'Portal unavailable for affected users.',
    (SELECT user_id FROM users WHERE username='end_user_2'),
    (SELECT user_id FROM users WHERE username='support_1'),
    (SELECT release_id FROM releases WHERE release_name='2026.2'),
    datetime('now', '-8 days'), datetime('now', '-2 days')
),
(3, 'Weekly revenue report exports blank CSV',
    'Scheduled report has headers but no rows.',
    'Reporting', 'Production', 'Medium', 'P2', 'Known Issue',
    (SELECT category_id FROM issue_categories WHERE category_name='Data Quality'),
    'RPT-CSV-009',
    'Run weekly report and download CSV.',
    'Rows should exist.', 'CSV is empty.', 'Finance manual reconciliation overhead.',
    (SELECT user_id FROM users WHERE username='support_1'),
    (SELECT user_id FROM users WHERE username='consultant_2'),
    (SELECT release_id FROM releases WHERE release_name='2026.2'),
    datetime('now', '-7 days'), datetime('now', '-4 days')
),
(4, 'Intermittent API 502 from order service',
    'Order API returns sporadic 502 under load spikes.',
    'Order API', 'Production', 'High', 'P1', 'Reopened',
    (SELECT category_id FROM issue_categories WHERE category_name='Infrastructure'),
    'ORD-API-502',
    'Simulate concurrent checkouts.',
    'Stable API responses.', 'Random 502 errors.', 'Checkout drop-offs increase.',
    (SELECT user_id FROM users WHERE username='support_2'),
    (SELECT user_id FROM users WHERE username='consultant_2'),
    (SELECT release_id FROM releases WHERE release_name='2026.2'),
    datetime('now', '-9 days'), datetime('now', '-1 days')
),
(5, 'Tax calculation mismatch for Canada',
    'Tax engine gives wrong totals for surcharge cases.',
    'Billing', 'Production', 'High', 'P1', 'New',
    (SELECT category_id FROM issue_categories WHERE category_name='Application Bug'),
    'TAX-CA-104',
    'Create Ontario invoice, discount, then surcharge.',
    'Tax should match configured formula.', 'Total differs by up to 2.4%.', 'Financial reporting risk.',
    (SELECT user_id FROM users WHERE username='end_user_1'),
    (SELECT user_id FROM users WHERE username='support_1'),
    (SELECT release_id FROM releases WHERE release_name='2026.2'),
    datetime('now', '-2 days'), datetime('now', '-2 days')
);

UPDATE issues
SET duplicate_of_issue_id = 1
WHERE issue_id = 5;

INSERT OR IGNORE INTO issue_status_history (issue_id, old_status, new_status, changed_by, changed_at, notes)
VALUES
(1, NULL, 'New', (SELECT user_id FROM users WHERE username='support_1'), datetime('now', '-10 days'), 'Initial ticket creation.'),
(1, 'New', 'In Progress', (SELECT user_id FROM users WHERE username='consultant_1'), datetime('now', '-9 days'), 'Investigation started.'),
(1, 'In Progress', 'Resolved', (SELECT user_id FROM users WHERE username='consultant_1'), datetime('now', '-7 days'), 'Fix deployed.'),
(4, NULL, 'New', (SELECT user_id FROM users WHERE username='support_2'), datetime('now', '-9 days'), 'Incident logged from traffic spike.'),
(4, 'New', 'In Progress', (SELECT user_id FROM users WHERE username='consultant_2'), datetime('now', '-8 days'), 'Ingress logs analyzed.'),
(4, 'In Progress', 'Resolved', (SELECT user_id FROM users WHERE username='consultant_2'), datetime('now', '-6 days'), 'Timeout values tuned.'),
(4, 'Resolved', 'Reopened', (SELECT user_id FROM users WHERE username='support_2'), datetime('now', '-3 days'), 'Regression under stress test.'),
(5, NULL, 'New', (SELECT user_id FROM users WHERE username='support_1'), datetime('now', '-2 days'), 'New customer report.');

INSERT OR IGNORE INTO resolutions (
    issue_id, root_cause, workaround, final_fix, resolution_steps, resolver_id, resolved_at, resolution_minutes, created_at, updated_at
)
VALUES
(1, 'Missing index and lock contention.', 'Retry posting during off-peak.',
    'Added index and adjusted transaction order.', 'Add index, deploy patch, reprocess failed invoices.',
    (SELECT user_id FROM users WHERE username='consultant_1'), datetime('now', '-7 days'), 420, datetime('now', '-7 days'), datetime('now', '-7 days')),
(3, 'ETL aggregation omitted weekly partitions.', 'Manual re-run with partition hints.',
    'Fixed partition filter and added data validation.', 'Patch query, rerun ETL, verify totals.',
    (SELECT user_id FROM users WHERE username='consultant_2'), datetime('now', '-5 days'), 190, datetime('now', '-5 days'), datetime('now', '-5 days'));

INSERT OR IGNORE INTO comments (issue_id, commented_by, comment_text, is_internal, created_at)
VALUES
(1, (SELECT user_id FROM users WHERE username='support_1'), 'Customer shared failing invoice IDs.', 'N', datetime('now', '-9 days')),
(1, (SELECT user_id FROM users WHERE username='consultant_1'), 'Deadlock pattern identified; patch prepared.', 'Y', datetime('now', '-8 days')),
(4, (SELECT user_id FROM users WHERE username='support_2'), 'Issue returned in load test at 280 RPS.', 'N', datetime('now', '-3 days'));

INSERT OR IGNORE INTO attachments (
    attachment_id, issue_id, original_filename, stored_filename, file_path, file_size_bytes, content_type, uploaded_by, uploaded_at
)
VALUES
(1, 1, 'invoice_failure_logs.txt', '20260401_203000_invoice_failure_logs.txt',
    'uploads/issue_1/20260401_203000_invoice_failure_logs.txt', 58231, 'text/plain',
    (SELECT user_id FROM users WHERE username='support_1'), datetime('now', '-9 days')),
(2, 4, 'ingress_502_spike.log', '20260411_144500_ingress_502_spike.log',
    'uploads/issue_4/20260411_144500_ingress_502_spike.log', 140890, 'text/plain',
    (SELECT user_id FROM users WHERE username='support_2'), datetime('now', '-3 days'));

INSERT OR IGNORE INTO linked_issues (issue_id, linked_issue_id, link_type, created_by, created_at)
VALUES
(5, 1, 'duplicate', (SELECT user_id FROM users WHERE username='support_1'), datetime('now', '-2 days')),
(2, 4, 'blocker', (SELECT user_id FROM users WHERE username='support_1'), datetime('now', '-7 days'));

INSERT OR IGNORE INTO issue_tag_map (issue_id, tag_id, created_by, created_at)
VALUES
(1, (SELECT tag_id FROM issue_tags WHERE tag_name='urgent'), (SELECT user_id FROM users WHERE username='support_1'), datetime('now', '-10 days')),
(1, (SELECT tag_id FROM issue_tags WHERE tag_name='billing'), (SELECT user_id FROM users WHERE username='support_1'), datetime('now', '-10 days')),
(4, (SELECT tag_id FROM issue_tags WHERE tag_name='api'), (SELECT user_id FROM users WHERE username='support_2'), datetime('now', '-9 days'));

INSERT OR IGNORE INTO solution_feedback (issue_id, resolution_id, user_id, rating, is_helpful, comments, created_at)
VALUES
(
    1,
    (SELECT resolution_id FROM resolutions WHERE issue_id = 1),
    (SELECT user_id FROM users WHERE username='end_user_1'),
    4.5, 'Y', 'Resolution steps were clear and useful.', datetime('now', '-6 days')
),
(
    3,
    (SELECT resolution_id FROM resolutions WHERE issue_id = 3),
    (SELECT user_id FROM users WHERE username='support_1'),
    4.2, 'Y', 'Fix worked with minor follow-up.', datetime('now', '-4 days')
);

INSERT OR IGNORE INTO knowledge_articles (issue_id, title, summary, article_body, created_by, published_at, is_published, helpful_votes)
VALUES
(
    1,
    'Handling ORA-20001 during invoice posting',
    'Guidance for deadlock-related ORA-20001 failures.',
    'Check lock waits, apply queue throttling, deploy index and transaction-order patch, then reprocess failed invoices.',
    (SELECT user_id FROM users WHERE username='consultant_1'),
    datetime('now', '-6 days'),
    'Y',
    14
);
