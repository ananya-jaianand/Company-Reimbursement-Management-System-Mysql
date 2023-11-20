use crms;

-- Insert data into Employee table
INSERT INTO Employee (Employee_Id, First_Name, Last_Name, Phone_No, Email, Department, Salary, Manager_Id)
VALUES
(1, 'John', 'Doe', 1234567890, 'john.doe@example.com', 'IT', 60000, NULL),
(2, 'Jane', 'Smith', 9876543210, 'jane.smith@example.com', 'HR', 55000, NULL),
(3, 'Alice', 'Johnson', 5551234567, 'alice.johnson@example.com', 'Finance', 70000, 1),
(4, 'Bob', 'Williams', 7779876543, 'bob.williams@example.com', 'Marketing', 65000, 1),
(5, 'Charlie', 'Miller', 3335557890, 'charlie.miller@example.com', 'IT', 62000, 2),
(6, 'Diana', 'Brown', 4449991234, 'diana.brown@example.com', 'HR', 58000, 2),
(7, 'Edward', 'Taylor', 6662223456, 'edward.taylor@example.com', 'Finance', 72000, 1),
(8, 'Fiona', 'Clark', 9998887766, 'fiona.clark@example.com', 'IT', 60000, 5),
(9, 'George', 'Wilson', 1113335555, 'george.wilson@example.com', 'Marketing', 67000, 5),
(10, 'Helen', 'Moore', 7774441111, 'helen.moore@example.com', 'HR', 59000, 6),
(11, 'Isaac', 'Anderson', 2227778888, 'isaac.anderson@example.com', 'IT', 63000, 7),
(12, 'Jasmine', 'Perez', 5556667777, 'jasmine.perez@example.com', 'Marketing', 68000, 7);

INSERT INTO Category (Category_Id, Category_Name, Maximum_Limit, Category_Percentage)
VALUES
(1, 'Travel', 500, 80),
(2, 'Meals', 100, 50),
(3, 'Office Supplies', 50, 40),
(4, 'Training', 300, 90),
(5, 'Miscellaneous', 200, 50),
(6, 'Conference Fees', 400, 75),
(7, 'Transportation', 150, 70),
(8, 'Lodging', 250, 75),
(9, 'Entertainment', 75, 60),
(10, 'Equipment', 350, 85);

-- Insert data into Status table
INSERT INTO Status (Status_Id, Status_Message)
VALUES
(1, 'Pending'),
(2, 'Approved'),
(3, 'Denied-Non-Compliance with Company Policy'),
(4, 'Denied-Lack of Sufficient Documentation'),
(5, 'Denied-Expense Not Business-Related'),
(6, 'Denied-Duplicate Submissions');

-- Insert data into Reimbursement table (10 entries)
INSERT INTO Reimbursement (Date_Submitted, Category_Id, Amount_Requested, Status_Id, Employee_Id)
VALUES
('2023-01-05', 2, 300, 1, 3),
('2023-02-20', 2, 75, 2, 9),
('2023-03-15', 3, 50, 2, 3),
('2023-04-10', 4, 200, 3, 4),
('2023-05-24', 1, 150, 2, 12),
('2023-06-20', 6, 350, 1, 6),
('2023-07-07', 7, 100, 4, 7),
('2023-08-23', 5, 200, 5, 8),
('2023-09-25', 9, 75, 2, 9),
('2023-10-11', 4, 300, 2, 3);

-- Insert data into Reimbursement_Document table
INSERT INTO Reimbursement_Document (Request_Id, Receipt_Id, Document_Date, Vendor_Name)
VALUES
(1, 'RCPT001', '2023-01-01', 'Restaurant A'),
(2, 'RCPT002', '2023-02-15', 'Restaurant B'),
(3, 'RCPT003', '2023-03-10', 'Office Supply Store C'),
(4, 'RCPT004', '2023-04-05', 'Training Institute D'),
(5, 'RCPT005', '2023-05-20', 'Travel Agency E'),
(6, 'RCPT006', '2023-06-12', 'Conference Organizer F'),
(7, 'RCPT007', '2023-07-05', 'Transportation Service G'),
(8, 'RCPT008', '2023-08-15', 'XYZ Shop'),
(9, 'RCPT009', '2023-09-15', 'Entertainment Venue I'),
(10, 'RCPT010', '2023-10-10', 'Training Institute J');





