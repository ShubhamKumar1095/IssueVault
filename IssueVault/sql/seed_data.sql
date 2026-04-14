-- IssueVault seed data
-- Seed password for all users: Password@123
-- Hash format: sha256$issuevaultseed$<digest>

INSERT INTO roles (role_name, description) VALUES ('end_user', 'Can submit and track own issues');
INSERT INTO roles (role_name, description) VALUES ('support_analyst', 'Can triage and update assigned issues');
INSERT INTO roles (role_name, description) VALUES ('consultant', 'Can investigate and resolve issues');
INSERT INTO roles (role_name, description) VALUES ('manager', 'Can view dashboards and reports');
INSERT INTO roles (role_name, description) VALUES ('admin', 'Can manage users, categories, and settings');

INSERT INTO teams (team_name, description) VALUES ('Customer Support', 'Frontline support');
INSERT INTO teams (team_name, description) VALUES ('Platform Engineering', 'Backend and infra');
INSERT INTO teams (team_name, description) VALUES ('Consulting', 'Investigation and resolution');
INSERT INTO teams (team_name, description) VALUES ('Management', 'Operational oversight');

INSERT INTO issue_categories (category_name, description) VALUES ('Application Bug', 'Defect in app behavior');
INSERT INTO issue_categories (category_name, description) VALUES ('Database', 'Data model and SQL runtime');
INSERT INTO issue_categories (category_name, description) VALUES ('Integration', 'External system and API');
INSERT INTO issue_categories (category_name, description) VALUES ('Infrastructure', 'Runtime and hosting');
INSERT INTO issue_categories (category_name, description) VALUES ('Data Quality', 'Incorrect data state');
INSERT INTO issue_categories (category_name, description) VALUES ('Configuration', 'Config and setup issue');

INSERT INTO issue_tags (tag_name) VALUES ('urgent');
INSERT INTO issue_tags (tag_name) VALUES ('customer-facing');
INSERT INTO issue_tags (tag_name) VALUES ('release-blocker');
INSERT INTO issue_tags (tag_name) VALUES ('billing');
INSERT INTO issue_tags (tag_name) VALUES ('api');

INSERT INTO releases (release_name, release_date, notes) VALUES ('2026.1', DATE '2026-01-15', 'Quarterly release');
INSERT INTO releases (release_name, release_date, notes) VALUES ('2026.2', DATE '2026-03-31', 'Stability release');

INSERT INTO users (username, full_name, email, password_hash, role_id, team_id)
VALUES ('end_user_1', 'Emma Reed', 'emma.reed@issuevault.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'end_user'),
        (SELECT team_id FROM teams WHERE team_name = 'Customer Support'));

INSERT INTO users (username, full_name, email, password_hash, role_id, team_id)
VALUES ('end_user_2', 'Noah James', 'noah.james@issuevault.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'end_user'),
        (SELECT team_id FROM teams WHERE team_name = 'Customer Support'));

INSERT INTO users (username, full_name, email, password_hash, role_id, team_id)
VALUES ('support_1', 'Ava Singh', 'ava.singh@issuevault.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'support_analyst'),
        (SELECT team_id FROM teams WHERE team_name = 'Customer Support'));

INSERT INTO users (username, full_name, email, password_hash, role_id, team_id)
VALUES ('support_2', 'Liam Park', 'liam.park@issuevault.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'support_analyst'),
        (SELECT team_id FROM teams WHERE team_name = 'Customer Support'));

INSERT INTO users (username, full_name, email, password_hash, role_id, team_id)
VALUES ('consultant_1', 'Mia Thompson', 'mia.thompson@issuevault.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'consultant'),
        (SELECT team_id FROM teams WHERE team_name = 'Consulting'));

INSERT INTO users (username, full_name, email, password_hash, role_id, team_id)
VALUES ('consultant_2', 'Ethan Alvarez', 'ethan.alvarez@issuevault.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'consultant'),
        (SELECT team_id FROM teams WHERE team_name = 'Consulting'));

INSERT INTO users (username, full_name, email, password_hash, role_id, team_id)
VALUES ('manager_1', 'Sophia Clarke', 'sophia.clarke@issuevault.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'manager'),
        (SELECT team_id FROM teams WHERE team_name = 'Management'));

INSERT INTO users (username, full_name, email, password_hash, role_id, team_id)
VALUES ('admin_1', 'Oliver Brooks', 'oliver.brooks@issuevault.local',
        'sha256$issuevaultseed$bf020c482d240201e077823b7b857a32e5899d8f4cd73dd000c2593f91624b26',
        (SELECT role_id FROM roles WHERE role_name = 'admin'),
        (SELECT team_id FROM teams WHERE team_name = 'Management'));

INSERT INTO issues (title, description, module_name, environment, severity, priority, status, category_id, error_code,
                    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at)
VALUES ('Invoice posting fails with ORA-20001',
        'Posting fails when tax adjustments are applied during close.',
        'Billing', 'Production', 'Critical', 'P1', 'Resolved',
        (SELECT category_id FROM issue_categories WHERE category_name = 'Database'),
        'ORA-20001',
        'Open invoice and submit posting with tax adjustment.',
        'Invoice should post.', 'Rollback with ORA-20001.', 'Month-end close blocked.',
        (SELECT user_id FROM users WHERE username = 'end_user_1'),
        (SELECT user_id FROM users WHERE username = 'consultant_1'),
        (SELECT release_id FROM releases WHERE release_name = '2026.1'),
        SYSTIMESTAMP - INTERVAL '10' DAY);

INSERT INTO issues (title, description, module_name, environment, severity, priority, status, category_id, error_code,
                    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at)
VALUES ('Login redirect loop after SSO timeout',
        'User redirects repeatedly between login and callback.',
        'Authentication', 'Production', 'High', 'P1', 'In Progress',
        (SELECT category_id FROM issue_categories WHERE category_name = 'Integration'),
        'AUTH-LOOP-17',
        'Expire session then open protected URL.',
        'Single redirect and return.', 'Infinite redirect loop.', 'Portal unavailable for affected users.',
        (SELECT user_id FROM users WHERE username = 'end_user_2'),
        (SELECT user_id FROM users WHERE username = 'support_1'),
        (SELECT release_id FROM releases WHERE release_name = '2026.2'),
        SYSTIMESTAMP - INTERVAL '8' DAY);

INSERT INTO issues (title, description, module_name, environment, severity, priority, status, category_id, error_code,
                    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at)
VALUES ('Weekly revenue report exports blank CSV',
        'Scheduled report has headers but no rows.',
        'Reporting', 'Production', 'Medium', 'P2', 'Known Issue',
        (SELECT category_id FROM issue_categories WHERE category_name = 'Data Quality'),
        'RPT-CSV-009',
        'Run weekly report and download CSV.',
        'Rows should exist.', 'CSV is empty.', 'Finance manual reconciliation overhead.',
        (SELECT user_id FROM users WHERE username = 'support_1'),
        (SELECT user_id FROM users WHERE username = 'consultant_2'),
        (SELECT release_id FROM releases WHERE release_name = '2026.2'),
        SYSTIMESTAMP - INTERVAL '7' DAY);

INSERT INTO issues (title, description, module_name, environment, severity, priority, status, category_id, error_code,
                    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at)
VALUES ('Payment gateway timeout in UAT',
        'Authorization requests timeout at 30 seconds.',
        'Payments', 'UAT', 'High', 'P2', 'Waiting for User',
        (SELECT category_id FROM issue_categories WHERE category_name = 'Integration'),
        'PG-TIMEOUT-30',
        'Run card payment flow in UAT.',
        'Response within SLA.', 'Client timeout.', 'UAT sign-off delayed.',
        (SELECT user_id FROM users WHERE username = 'support_2'),
        (SELECT user_id FROM users WHERE username = 'consultant_1'),
        (SELECT release_id FROM releases WHERE release_name = '2026.2'),
        SYSTIMESTAMP - INTERVAL '6' DAY);

INSERT INTO issues (title, description, module_name, environment, severity, priority, status, category_id, error_code,
                    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at)
VALUES ('Catalog sync job creates duplicate SKUs',
        'Nightly sync duplicates variant rows.',
        'Catalog', 'Production', 'High', 'P1', 'Resolved',
        (SELECT category_id FROM issue_categories WHERE category_name = 'Data Quality'),
        'CAT-SYNC-222',
        'Run nightly sync and compare counts.',
        'One active row per SKU.', 'Duplicate rows exist.', 'Order and pricing mismatches.',
        (SELECT user_id FROM users WHERE username = 'support_1'),
        (SELECT user_id FROM users WHERE username = 'consultant_2'),
        (SELECT release_id FROM releases WHERE release_name = '2026.1'),
        SYSTIMESTAMP - INTERVAL '13' DAY);

INSERT INTO issues (title, description, module_name, environment, severity, priority, status, category_id, error_code,
                    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at)
VALUES ('SLA breach alerts not triggering',
        'P1 breach alerts are not emitted in high queue periods.',
        'Monitoring', 'Production', 'Critical', 'P1', 'Closed',
        (SELECT category_id FROM issue_categories WHERE category_name = 'Configuration'),
        'SLA-ALERT-88',
        'Create multiple P1 incidents and wait for SLA breach.',
        'Alert should be posted.', 'No alert emitted.', 'Escalation compliance risk.',
        (SELECT user_id FROM users WHERE username = 'manager_1'),
        (SELECT user_id FROM users WHERE username = 'consultant_1'),
        (SELECT release_id FROM releases WHERE release_name = '2026.1'),
        SYSTIMESTAMP - INTERVAL '18' DAY);

INSERT INTO issues (title, description, module_name, environment, severity, priority, status, category_id, error_code,
                    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at)
VALUES ('Intermittent API 502 from order service',
        'Order API returns sporadic 502 under load spikes.',
        'Order API', 'Production', 'High', 'P1', 'Reopened',
        (SELECT category_id FROM issue_categories WHERE category_name = 'Infrastructure'),
        'ORD-API-502',
        'Simulate 300 concurrent checkouts.',
        'Stable API responses.', 'Random 502 errors.', 'Checkout drop-offs increase.',
        (SELECT user_id FROM users WHERE username = 'support_2'),
        (SELECT user_id FROM users WHERE username = 'consultant_2'),
        (SELECT release_id FROM releases WHERE release_name = '2026.2'),
        SYSTIMESTAMP - INTERVAL '9' DAY);

INSERT INTO issues (title, description, module_name, environment, severity, priority, status, category_id, error_code,
                    steps_to_reproduce, expected_result, actual_result, business_impact, reported_by, assigned_to, release_id, created_at)
VALUES ('Tax calculation mismatch for Canada',
        'Tax engine gives wrong totals for some provincial surcharge cases.',
        'Billing', 'Production', 'High', 'P1', 'New',
        (SELECT category_id FROM issue_categories WHERE category_name = 'Application Bug'),
        'TAX-CA-104',
        'Create Ontario invoice, discount, then surcharge.',
        'Tax should match configured formula.', 'Total differs by up to 2.4%.', 'Financial reporting risk.',
        (SELECT user_id FROM users WHERE username = 'end_user_1'),
        (SELECT user_id FROM users WHERE username = 'support_1'),
        (SELECT release_id FROM releases WHERE release_name = '2026.2'),
        SYSTIMESTAMP - INTERVAL '2' DAY);

INSERT INTO issue_status_history (issue_id, old_status, new_status, changed_by, changed_at, notes)
SELECT issue_id, NULL, 'New', (SELECT user_id FROM users WHERE username = 'support_1'),
       SYSTIMESTAMP - INTERVAL '10' DAY, 'Initial ticket creation.'
FROM issues WHERE title = 'Invoice posting fails with ORA-20001';

INSERT INTO issue_status_history (issue_id, old_status, new_status, changed_by, changed_at, notes)
SELECT issue_id, 'New', 'In Progress', (SELECT user_id FROM users WHERE username = 'consultant_1'),
       SYSTIMESTAMP - INTERVAL '9' DAY, 'Investigation started.'
FROM issues WHERE title = 'Invoice posting fails with ORA-20001';

INSERT INTO issue_status_history (issue_id, old_status, new_status, changed_by, changed_at, notes)
SELECT issue_id, 'In Progress', 'Resolved', (SELECT user_id FROM users WHERE username = 'consultant_1'),
       SYSTIMESTAMP - INTERVAL '7' DAY, 'Fix deployed.'
FROM issues WHERE title = 'Invoice posting fails with ORA-20001';

INSERT INTO issue_status_history (issue_id, old_status, new_status, changed_by, changed_at, notes)
SELECT issue_id, NULL, 'New', (SELECT user_id FROM users WHERE username = 'support_2'),
       SYSTIMESTAMP - INTERVAL '9' DAY, 'Incident logged from traffic spike.'
FROM issues WHERE title = 'Intermittent API 502 from order service';

INSERT INTO issue_status_history (issue_id, old_status, new_status, changed_by, changed_at, notes)
SELECT issue_id, 'New', 'In Progress', (SELECT user_id FROM users WHERE username = 'consultant_2'),
       SYSTIMESTAMP - INTERVAL '8' DAY, 'Ingress and service logs analyzed.'
FROM issues WHERE title = 'Intermittent API 502 from order service';

INSERT INTO issue_status_history (issue_id, old_status, new_status, changed_by, changed_at, notes)
SELECT issue_id, 'In Progress', 'Resolved', (SELECT user_id FROM users WHERE username = 'consultant_2'),
       SYSTIMESTAMP - INTERVAL '6' DAY, 'Timeout values tuned.'
FROM issues WHERE title = 'Intermittent API 502 from order service';

INSERT INTO issue_status_history (issue_id, old_status, new_status, changed_by, changed_at, notes)
SELECT issue_id, 'Resolved', 'Reopened', (SELECT user_id FROM users WHERE username = 'support_2'),
       SYSTIMESTAMP - INTERVAL '3' DAY, 'Regression under stress test.'
FROM issues WHERE title = 'Intermittent API 502 from order service';

INSERT INTO resolutions (issue_id, root_cause, workaround, final_fix, resolution_steps, resolver_id, resolved_at, resolution_minutes)
SELECT issue_id, 'Missing index and lock contention.',
       'Retry posting during off-peak.',
       'Added index and adjusted transaction order.',
       'Add index, deploy patch, reprocess failed invoices.',
       (SELECT user_id FROM users WHERE username = 'consultant_1'),
       SYSTIMESTAMP - INTERVAL '7' DAY, 420
FROM issues WHERE title = 'Invoice posting fails with ORA-20001';

INSERT INTO resolutions (issue_id, root_cause, workaround, final_fix, resolution_steps, resolver_id, resolved_at, resolution_minutes)
SELECT issue_id, 'Merge key mapping bug.',
       'Run nightly dedup as workaround.',
       'Updated merge key and uniqueness guard.',
       'Patch ETL SQL, run backfill, validate counts.',
       (SELECT user_id FROM users WHERE username = 'consultant_2'),
       SYSTIMESTAMP - INTERVAL '11' DAY, 310
FROM issues WHERE title = 'Catalog sync job creates duplicate SKUs';

INSERT INTO resolutions (issue_id, root_cause, workaround, final_fix, resolution_steps, resolver_id, resolved_at, resolution_minutes)
SELECT issue_id, 'Threshold parser ignored unit token.',
       'Hourly manual SLA review.',
       'Parser corrected and regression test added.',
       'Deploy parser fix, replay events, verify alerts.',
       (SELECT user_id FROM users WHERE username = 'consultant_1'),
       SYSTIMESTAMP - INTERVAL '16' DAY, 280
FROM issues WHERE title = 'SLA breach alerts not triggering';

INSERT INTO comments (issue_id, commented_by, comment_text, is_internal, created_at)
SELECT issue_id, (SELECT user_id FROM users WHERE username = 'support_1'),
       'Customer shared failing invoice IDs from peak processing.', 'N', SYSTIMESTAMP - INTERVAL '9' DAY
FROM issues WHERE title = 'Invoice posting fails with ORA-20001';

INSERT INTO comments (issue_id, commented_by, comment_text, is_internal, created_at)
SELECT issue_id, (SELECT user_id FROM users WHERE username = 'consultant_1'),
       'Deadlock pattern identified; patch prepared.', 'Y', SYSTIMESTAMP - INTERVAL '8' DAY
FROM issues WHERE title = 'Invoice posting fails with ORA-20001';

INSERT INTO comments (issue_id, commented_by, comment_text, is_internal, created_at)
SELECT issue_id, (SELECT user_id FROM users WHERE username = 'support_2'),
       'Issue returned in load test at 280 RPS.', 'N', SYSTIMESTAMP - INTERVAL '3' DAY
FROM issues WHERE title = 'Intermittent API 502 from order service';

INSERT INTO attachments (issue_id, original_filename, stored_filename, file_path, file_size_bytes, content_type, uploaded_by, uploaded_at)
SELECT issue_id, 'invoice_failure_logs.txt', '20260401_203000_invoice_failure_logs.txt',
       'uploads/issue_1/20260401_203000_invoice_failure_logs.txt', 58231, 'text/plain',
       (SELECT user_id FROM users WHERE username = 'support_1'), SYSTIMESTAMP - INTERVAL '9' DAY
FROM issues WHERE title = 'Invoice posting fails with ORA-20001';

INSERT INTO attachments (issue_id, original_filename, stored_filename, file_path, file_size_bytes, content_type, uploaded_by, uploaded_at)
SELECT issue_id, 'ingress_502_spike.log', '20260411_144500_ingress_502_spike.log',
       'uploads/issue_8/20260411_144500_ingress_502_spike.log', 140890, 'text/plain',
       (SELECT user_id FROM users WHERE username = 'support_2'), SYSTIMESTAMP - INTERVAL '3' DAY
FROM issues WHERE title = 'Intermittent API 502 from order service';

INSERT INTO linked_issues (issue_id, linked_issue_id, link_type, created_by, created_at)
VALUES (
    (SELECT issue_id FROM issues WHERE title = 'Tax calculation mismatch for Canada'),
    (SELECT issue_id FROM issues WHERE title = 'Invoice posting fails with ORA-20001'),
    'duplicate',
    (SELECT user_id FROM users WHERE username = 'support_1'),
    SYSTIMESTAMP - INTERVAL '2' DAY
);

INSERT INTO linked_issues (issue_id, linked_issue_id, link_type, created_by, created_at)
VALUES (
    (SELECT issue_id FROM issues WHERE title = 'Login redirect loop after SSO timeout'),
    (SELECT issue_id FROM issues WHERE title = 'Intermittent API 502 from order service'),
    'blocker',
    (SELECT user_id FROM users WHERE username = 'support_1'),
    SYSTIMESTAMP - INTERVAL '7' DAY
);

INSERT INTO issue_tag_map (issue_id, tag_id, created_by, created_at)
VALUES (
    (SELECT issue_id FROM issues WHERE title = 'Invoice posting fails with ORA-20001'),
    (SELECT tag_id FROM issue_tags WHERE tag_name = 'urgent'),
    (SELECT user_id FROM users WHERE username = 'support_1'),
    SYSTIMESTAMP - INTERVAL '10' DAY
);

INSERT INTO issue_tag_map (issue_id, tag_id, created_by, created_at)
VALUES (
    (SELECT issue_id FROM issues WHERE title = 'Intermittent API 502 from order service'),
    (SELECT tag_id FROM issue_tags WHERE tag_name = 'api'),
    (SELECT user_id FROM users WHERE username = 'support_2'),
    SYSTIMESTAMP - INTERVAL '9' DAY
);

INSERT INTO solution_feedback (issue_id, resolution_id, user_id, rating, is_helpful, comments, created_at)
VALUES (
    (SELECT issue_id FROM issues WHERE title = 'Invoice posting fails with ORA-20001'),
    (SELECT resolution_id FROM resolutions WHERE issue_id = (SELECT issue_id FROM issues WHERE title = 'Invoice posting fails with ORA-20001')),
    (SELECT user_id FROM users WHERE username = 'end_user_1'),
    4.5, 'Y', 'Resolution steps were clear and useful.', SYSTIMESTAMP - INTERVAL '6' DAY
);

INSERT INTO solution_feedback (issue_id, resolution_id, user_id, rating, is_helpful, comments, created_at)
VALUES (
    (SELECT issue_id FROM issues WHERE title = 'Catalog sync job creates duplicate SKUs'),
    (SELECT resolution_id FROM resolutions WHERE issue_id = (SELECT issue_id FROM issues WHERE title = 'Catalog sync job creates duplicate SKUs')),
    (SELECT user_id FROM users WHERE username = 'support_1'),
    4.0, 'Y', 'Fix worked well with minor follow-up.', SYSTIMESTAMP - INTERVAL '10' DAY
);

INSERT INTO knowledge_articles (issue_id, title, summary, article_body, created_by, published_at, is_published, helpful_votes)
VALUES (
    (SELECT issue_id FROM issues WHERE title = 'Invoice posting fails with ORA-20001'),
    'Handling ORA-20001 during invoice posting',
    'Guidance for deadlock-related ORA-20001 failures.',
    'Check lock waits, apply temporary queue throttling, deploy index and transaction-order patch, then reprocess failed invoices.',
    (SELECT user_id FROM users WHERE username = 'consultant_1'),
    SYSTIMESTAMP - INTERVAL '6' DAY,
    'Y',
    14
);

UPDATE issues
SET duplicate_of_issue_id = (SELECT issue_id FROM issues WHERE title = 'Invoice posting fails with ORA-20001')
WHERE title = 'Tax calculation mismatch for Canada';

COMMIT;
