-- Equipment Requests Table
CREATE TABLE IF NOT EXISTS equipment_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    request_date DATETIME NOT NULL,
    response_date DATETIME,
    requester_id INTEGER,
    notes TEXT,
    FOREIGN KEY (requester_id) REFERENCES users(userID)
);

-- Purchase Requests Table
CREATE TABLE IF NOT EXISTS purchase_requests (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    request_date DATETIME NOT NULL,
    approval_date DATETIME,
    requester_id INTEGER,
    justification TEXT,
    FOREIGN KEY (requester_id) REFERENCES users(userID)
);

-- IT Staff Notifications Table
CREATE TABLE IF NOT EXISTS it_staff_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER,
    equipment_details TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    notification_date DATETIME NOT NULL,
    processed_date DATETIME,
    processed_by INTEGER,
    notes TEXT,
    FOREIGN KEY (request_id) REFERENCES equipment_requests(request_id),
    FOREIGN KEY (processed_by) REFERENCES users(userID)
);

-- Drop existing indexes if they exist
DROP INDEX IF EXISTS idx_equipment_requests_status;
DROP INDEX IF EXISTS idx_purchase_requests_status;
DROP INDEX IF EXISTS idx_notifications_status;

-- Recreate indexes
CREATE INDEX IF NOT EXISTS idx_equipment_requests_status ON equipment_requests(status);
CREATE INDEX IF NOT EXISTS idx_purchase_requests_status ON purchase_requests(status);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON it_staff_notifications(status);

-- Labs Table
CREATE TABLE IF NOT EXISTS labs (
    labID TEXT PRIMARY KEY,
    size INTEGER NOT NULL,
    location TEXT NOT NULL,
    info TEXT,
    isAvailable BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Delete existing lab data to avoid conflicts
DELETE FROM labs;

-- Insert sample labs
INSERT INTO labs (labID, size, location, info) VALUES
('LAB001', 30, 'Building A, Floor 1', 'General Purpose Lab'),
('LAB002', 25, 'Building A, Floor 2', 'Programming Lab'),
('LAB003', 20, 'Building B, Floor 1', 'Hardware Lab');

-- Create equipment_issues table with all needed columns
CREATE TABLE IF NOT EXISTS equipment_issues (
    issueID INTEGER PRIMARY KEY AUTOINCREMENT,
    equipID INTEGER,
    description TEXT,
    report_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_date DATETIME,
    reported_by INTEGER,
    resolution TEXT,
    resolved_by INTEGER,
    FOREIGN KEY (equipID) REFERENCES equipment(equipID),
    FOREIGN KEY (reported_by) REFERENCES users(userID),
    FOREIGN KEY (resolved_by) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS inventory_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',
    response_date DATETIME,
    notes TEXT
);