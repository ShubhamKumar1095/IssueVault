-- ResolveHub SQLite schema

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    team_id INTEGER,
    is_active TEXT NOT NULL DEFAULT 'Y' CHECK (is_active IN ('Y', 'N')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TEXT,
    FOREIGN KEY (role_id) REFERENCES roles (role_id),
    FOREIGN KEY (team_id) REFERENCES teams (team_id)
);

CREATE TABLE IF NOT EXISTS issue_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active TEXT NOT NULL DEFAULT 'Y' CHECK (is_active IN ('Y', 'N'))
);

CREATE TABLE IF NOT EXISTS issue_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS releases (
    release_id INTEGER PRIMARY KEY AUTOINCREMENT,
    release_name TEXT NOT NULL UNIQUE,
    release_date TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    module_name TEXT NOT NULL,
    environment TEXT,
    severity TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    priority TEXT NOT NULL CHECK (priority IN ('P1', 'P2', 'P3', 'P4')),
    status TEXT NOT NULL DEFAULT 'New' CHECK (
        status IN (
            'New',
            'Under Review',
            'Known Issue',
            'In Progress',
            'Waiting for User',
            'Resolved',
            'Closed',
            'Reopened'
        )
    ),
    category_id INTEGER NOT NULL,
    error_code TEXT,
    steps_to_reproduce TEXT,
    expected_result TEXT,
    actual_result TEXT,
    business_impact TEXT,
    reported_by INTEGER NOT NULL,
    assigned_to INTEGER,
    release_id INTEGER,
    duplicate_of_issue_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES issue_categories (category_id),
    FOREIGN KEY (reported_by) REFERENCES users (user_id),
    FOREIGN KEY (assigned_to) REFERENCES users (user_id),
    FOREIGN KEY (release_id) REFERENCES releases (release_id),
    FOREIGN KEY (duplicate_of_issue_id) REFERENCES issues (issue_id)
);

CREATE TABLE IF NOT EXISTS issue_status_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL CHECK (
        new_status IN (
            'New',
            'Under Review',
            'Known Issue',
            'In Progress',
            'Waiting for User',
            'Resolved',
            'Closed',
            'Reopened'
        )
    ),
    changed_by INTEGER NOT NULL,
    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS issue_tag_map (
    issue_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (issue_id, tag_id),
    FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES issue_tags (tag_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    content_type TEXT,
    uploaded_by INTEGER NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    commented_by INTEGER NOT NULL,
    comment_text TEXT NOT NULL,
    is_internal TEXT NOT NULL DEFAULT 'N' CHECK (is_internal IN ('Y', 'N')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE,
    FOREIGN KEY (commented_by) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS resolutions (
    resolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL UNIQUE,
    root_cause TEXT NOT NULL,
    workaround TEXT,
    final_fix TEXT NOT NULL,
    resolution_steps TEXT NOT NULL,
    resolver_id INTEGER NOT NULL,
    resolved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolution_minutes INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE,
    FOREIGN KEY (resolver_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS linked_issues (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    linked_issue_id INTEGER NOT NULL,
    link_type TEXT NOT NULL CHECK (link_type IN ('duplicate', 'parent', 'dependent', 'recurring', 'blocker')),
    created_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (issue_id, linked_issue_id, link_type),
    CHECK (issue_id <> linked_issue_id),
    FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE,
    FOREIGN KEY (linked_issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS solution_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    resolution_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating REAL NOT NULL CHECK (rating BETWEEN 1 AND 5),
    is_helpful TEXT NOT NULL DEFAULT 'Y' CHECK (is_helpful IN ('Y', 'N')),
    comments TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE,
    FOREIGN KEY (resolution_id) REFERENCES resolutions (resolution_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS knowledge_articles (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER,
    title TEXT NOT NULL,
    summary TEXT,
    article_body TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    published_at TEXT,
    is_published TEXT NOT NULL DEFAULT 'N' CHECK (is_published IN ('Y', 'N')),
    helpful_votes INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (issue_id) REFERENCES issues (issue_id),
    FOREIGN KEY (created_by) REFERENCES users (user_id)
);

CREATE INDEX IF NOT EXISTS idx_issues_title_upper ON issues (title);
CREATE INDEX IF NOT EXISTS idx_issues_error_code ON issues (error_code);
CREATE INDEX IF NOT EXISTS idx_issues_module_name ON issues (module_name);
CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues (severity);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues (status);
CREATE INDEX IF NOT EXISTS idx_issues_created_at ON issues (created_at);
CREATE INDEX IF NOT EXISTS idx_issues_assigned_to ON issues (assigned_to);

CREATE INDEX IF NOT EXISTS idx_comments_issue ON comments (issue_id, created_at);
CREATE INDEX IF NOT EXISTS idx_status_history_issue ON issue_status_history (issue_id, changed_at);
CREATE INDEX IF NOT EXISTS idx_solution_feedback_issue ON solution_feedback (issue_id);
CREATE INDEX IF NOT EXISTS idx_attachments_issue ON attachments (issue_id);
