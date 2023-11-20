CREATE DATABASE IF NOT EXISTS crms;
use crms;
CREATE TABLE IF NOT EXISTS Employee (
    Employee_Id INT PRIMARY KEY,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Phone_No VARCHAR(15) NOT NULL,
    Email VARCHAR(100),
    Department VARCHAR(50) NOT NULL,
    Salary INT NOT NULL,
    Manager_Id INT,
    FOREIGN KEY (Manager_Id) REFERENCES Employee (Employee_Id)
);

CREATE TABLE IF NOT EXISTS Category (
    Category_Id INT PRIMARY KEY,
    Category_Name VARCHAR(50) NOT NULL,
    Maximum_Limit INT NOT NULL,
    Category_Percentage INT NOT NULL
);



CREATE TABLE IF NOT EXISTS Status (
    Status_Id INT PRIMARY KEY,
    Status_Message VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Reimbursement (
    Request_Id INT AUTO_INCREMENT PRIMARY KEY,
    Date_Submitted DATE NOT NULL,
    Category_Id INT NOT NULL,
    Amount_Requested DECIMAL(10, 2) NOT NULL,
    Status_Id INT DEFAULT 1 NOT NULL,
    Employee_Id INT NOT NULL,
    FOREIGN KEY (Employee_Id) REFERENCES Employee(Employee_Id),
    FOREIGN KEY (Category_Id) REFERENCES Category(Category_Id),
    FOREIGN KEY (Status_Id) REFERENCES Status(Status_Id)
    
);
CREATE TABLE IF NOT EXISTS Payment (
    Payment_Id INT AUTO_INCREMENT PRIMARY KEY,
    Request_Id INT NOT NULL ,
    Payment_Date DATE NOT NULL,
    Payment_Amt DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (Request_Id) REFERENCES Reimbursement(Request_Id)
);

CREATE TABLE IF NOT EXISTS Notification (
    Notification_Id INT AUTO_INCREMENT PRIMARY KEY,
    Request_Id INT NOT NULL,
    Date_Sent DATETIME NOT NULL,
    Message_ VARCHAR(100) NOT NULL,
    FOREIGN KEY (Request_Id) REFERENCES Reimbursement(Request_Id)
    
);

CREATE TABLE IF NOT EXISTS Reimbursement_Document (
    Document_Id INT AUTO_INCREMENT PRIMARY KEY,
    Request_Id INT NOT NULL,
    Receipt_Id VARCHAR(50) NOT NULL,
    Document_Date DATE NOT NULL,
    Vendor_Name VARCHAR(50) NOT NULL,
    FOREIGN KEY (Request_Id) REFERENCES Reimbursement(Request_Id)
);

-- Create a trigger to insert into Payment table when a reimbursement is approved
DELIMITER //
CREATE TRIGGER before_reimbursement_approval
AFTER INSERT ON Reimbursement
FOR EACH ROW
BEGIN
    -- Check if the status is updated to approved (Status_Id = 2)
    IF NEW.Status_Id = 2 THEN
        -- Calculate payment amount based on the category percentage
        INSERT INTO Payment (Request_Id, Payment_Date, Payment_Amt)
        SELECT NEW.Request_Id, CURDATE(), 
            CASE 
                WHEN NEW.Amount_Requested * Category_Percentage / 100 > Category.Maximum_Limit 
                THEN Category.Maximum_Limit
                ELSE NEW.Amount_Requested * Category_Percentage / 100
            END
        FROM Category
        WHERE Category.Category_Id = NEW.Category_Id;
    END IF;
END;
//
DELIMITER ;


-- Create a trigger to insert into Payment table when a reimbursement is approved
DELIMITER //
CREATE TRIGGER after_reimbursement_approval
AFTER UPDATE ON Reimbursement
FOR EACH ROW
BEGIN
    -- Check if the status is updated to approved (Status_Id = 2)
    IF NEW.Status_Id = 2 THEN
        -- Calculate payment amount based on the category percentage
        INSERT INTO Payment (Request_Id, Payment_Date, Payment_Amt)
        SELECT NEW.Request_Id, CURDATE(), 
            CASE 
                WHEN NEW.Amount_Requested * Category_Percentage / 100 > Category.Maximum_Limit 
                THEN Category.Maximum_Limit
                ELSE NEW.Amount_Requested * Category_Percentage / 100
            END
        FROM Category
        WHERE Category.Category_Id = NEW.Category_Id;
    END IF;
END;
//
DELIMITER ;

-- Create a trigger to update Notification table when a reimbursement is approved or denied
DELIMITER //
CREATE TRIGGER before_reimbursement_approval_or_denial
AFTER INSERT ON Reimbursement
FOR EACH ROW
BEGIN
    -- Check if the status is updated to approved (Status_Id = 2) or denied
    IF NEW.Status_Id = 2 OR NEW.Status_Id = 3 OR NEW.Status_Id = 4 OR NEW.Status_Id = 5 OR NEW.Status_Id = 6 THEN
        -- Insert into Notification table with the respective data
        INSERT INTO Notification (Request_Id, Date_Sent, Message_)
        VALUES (NEW.Request_Id, CURDATE(), (SELECT Status_Message FROM Status WHERE Status_Id = NEW.Status_Id));
    END IF;
END;
//
DELIMITER ;


-- Create a trigger to update Notification table when a reimbursement is approved or denied
DELIMITER //
CREATE TRIGGER after_reimbursement_approval_or_denial
AFTER UPDATE ON Reimbursement
FOR EACH ROW
BEGIN
    -- Check if the status is updated to approved (Status_Id = 2) or denied
    IF NEW.Status_Id = 2 OR NEW.Status_Id = 3 OR NEW.Status_Id = 4 OR NEW.Status_Id = 5 OR NEW.Status_Id = 6 THEN
        -- Insert into Notification table with the respective data
        INSERT INTO Notification (Request_Id, Date_Sent, Message_)
        VALUES (NEW.Request_Id, CURDATE(), (SELECT Status_Message FROM Status WHERE Status_Id = NEW.Status_Id));
    END IF;
END;
//
DELIMITER ;

DELIMITER //

CREATE PROCEDURE UpdateReimbursementStatus(IN p_request_id INT, IN p_new_status_message VARCHAR(255))
BEGIN
    DECLARE status_id_val INT;

    -- Get the Status_Id for the provided status message
    SELECT Status_Id INTO status_id_val FROM Status WHERE Status_Message = p_new_status_message;

    -- Update the Reimbursement status
    UPDATE Reimbursement SET Status_Id = status_id_val WHERE Request_Id = p_request_id;
END //

DELIMITER ;








