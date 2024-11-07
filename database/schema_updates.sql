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

-- Add indexes for better performance
CREATE INDEX idx_equipment_requests_status ON equipment_requests(status);
CREATE INDEX idx_purchase_requests_status ON purchase_requests(status);
CREATE INDEX idx_notifications_status ON it_staff_notifications(status);