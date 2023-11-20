import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

# Establish database connection
conn = mysql.connector.connect(
    host='localhost',
    user='aj',
    password='pwd',
    database='crms'
)
cursor = conn.cursor()

# Function to submit a new reimbursement and associated documents
def submit_reimbursement(employee_id, category_id, amount_requested,receipt_id, document_date, vendor_name):
    current_date = datetime.now().date()
    status = 1  # Default status_id is 1 (Pending)

    # Insert into Reimbursement table
    reimbursement_query = """
    INSERT INTO Reimbursement (Date_Submitted, Category_Id, Amount_Requested, Status_Id, Employee_Id)
    VALUES (%s, %s, %s, %s, %s)
    """

    # Insert into Reimbursement_Document table
    reimbursement_doc_query = """
    INSERT INTO Reimbursement_Document (Request_Id, Receipt_Id, Document_Date, Vendor_Name)
    VALUES (LAST_INSERT_ID(), %s, %s, %s)
    """

    with conn.cursor() as cursor:
        # Insert into Reimbursement table
        cursor.execute(reimbursement_query, (current_date, category_id, amount_requested, status, employee_id))

        # Insert into Reimbursement_Document table
        cursor.execute(reimbursement_doc_query, (receipt_id, document_date, vendor_name))

        # Commit changes
        conn.commit()


# Function to retract a reimbursement
def retract_reimbursement(request_id):
    # Delete entry from Reimbursement_Document table
    query_delete_doc = "DELETE FROM Reimbursement_Document WHERE Request_Id = %s"
    
    # Delete entry from Reimbursement table
    query_delete_reimb = "DELETE FROM Reimbursement WHERE Request_Id = %s"

    with conn.cursor() as cursor:
        # Delete from Reimbursement_Document
        cursor.execute(query_delete_doc, (request_id,))
        
        # Delete from Reimbursement
        cursor.execute(query_delete_reimb, (request_id,))
        
        conn.commit()


# Function to change a current reimbursement and its document
def change_reimbursement(request_id, new_amount, new_category_id, new_receipt_id, new_document_date, new_vendor_name):
    # Update entry in Reimbursement table
    query_update_reimb = "UPDATE Reimbursement SET Amount_Requested = %s, Category_ID = %s WHERE Request_Id = %s"
    
    # Update entry in Reimbursement_Document table
    query_update_doc = "UPDATE Reimbursement_Document SET Receipt_Id = %s, Document_Date = %s, Vendor_Name = %s WHERE Request_Id = %s"

    with conn.cursor() as cursor:
        # Update Reimbursement table
        cursor.execute(query_update_reimb, (new_amount, new_category_id, request_id))

        # Update Reimbursement_Document table
        cursor.execute(query_update_doc, (new_receipt_id, new_document_date, new_vendor_name, request_id))
        
        # Commit the changes to the database
        conn.commit()


def get_reimbursement_history(employee_id):
    query = """
    SELECT
        R.Request_Id,
        R.Date_Submitted,
        C.Category_Name,
        R.Amount_Requested,
        CASE
            WHEN R.Status_Id = 2 THEN 'Approved'
            WHEN R.Status_Id IN (3, 4, 5, 6) THEN CONCAT('', S.Status_Message)
            ELSE 'Pending'
        END AS Status,
        RD.Vendor_Name,
        RD.Receipt_Id
    FROM
        Reimbursement R
    JOIN
        Category C ON R.Category_Id = C.Category_Id
    JOIN
        Status S ON R.Status_Id = S.Status_Id
    LEFT JOIN
        Reimbursement_Document RD ON R.Request_Id = RD.Request_Id
    WHERE
        R.Employee_Id = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (employee_id,))
        result = cursor.fetchall()

        # Fetch column names from the description attribute
        column_names = ["Request ID", "Date Submitted", "Category Name", "Amount Requested", "Status", "Vendor Name", "Receipt ID"]

    return result, column_names

# Function to get details of approved reimbursements with aggregate totals
def get_approved_reimbursement_details(employee_id):
    query = """
    SELECT
        R.Request_Id,
        R.Date_Submitted,
        C.Category_Name,
        R.Amount_Requested,
        P.Payment_Amt,
        P.Payment_Date,
        RD.Vendor_Name,
        RD.Receipt_Id
    FROM
        Reimbursement R
    JOIN
        Category C ON R.Category_Id = C.Category_Id
    JOIN
        Status S ON R.Status_Id = S.Status_Id
    LEFT JOIN
        Reimbursement_Document RD ON R.Request_Id = RD.Request_Id
    LEFT JOIN
        Payment P ON R.Request_Id = P.Request_Id
    WHERE
        R.Employee_Id = %s
        AND R.Status_Id = 2  -- Filter for approved reimbursements
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (employee_id,))
        result = cursor.fetchall()

        # Fetch column names from the description attribute
        column_names = ["Request ID", "Date Submitted", "Category Name", "Amount Requested", "Amount Reimbursed", "Payment Date", "Vendor Name", "Receipt ID"]

    return result, column_names

# Function to display the section for approved reimbursement details
def display_approved_reimbursement_details(employee_id):
    st.header("Approved Reimbursement Details")

    approved_reimbursement_details, column_names = get_approved_reimbursement_details(employee_id)

    if approved_reimbursement_details:
        df = pd.DataFrame(approved_reimbursement_details, columns=column_names)

        # Rename columns
        df = df.rename(columns={
            "Request_Id": "Request ID",
            "Date_Submitted": "Date Submitted",
            "Category_Name": "Category Name",
            "Amount_Requested": "Amount Requested",
            "Payment_Amt": "Amount Reimbursed",
            "Payment_Date": "Payment Date",
            "Vendor_Name": "Vendor Name",
            "Receipt_Id": "Receipt ID"
        })

        # Display the dataframe
        st.dataframe(df, height=200)

    else:
        st.warning("No approved reimbursement details found.")


def get_approved_reimbursement_details_total(employee_id):
    query = """
    SELECT
        R.Employee_Id,
        R.Status_Id,
        SUM(R.Amount_Requested) AS Total_Amount_Requested,
        COALESCE(SUM(P.Payment_Amt), 0) AS Total_Amount_Reimbursed
    FROM
        Reimbursement R
    LEFT JOIN
        Payment P ON R.Request_Id = P.Request_Id
    WHERE
        R.Employee_Id = %s
        AND R.Status_Id = 2  -- Filter for approved reimbursements
    GROUP BY
        R.Employee_Id, R.Status_Id
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (employee_id,))
        result = cursor.fetchone()

    return result



def display_approved_reimbursement_details_total(employee_id):

    approved_reimbursement_details = get_approved_reimbursement_details_total(employee_id)

    if approved_reimbursement_details:
        employee_id, status_id, total_amount_requested, total_amount_reimbursed = approved_reimbursement_details

        # st.write(f"Employee ID: {employee_id}")
        st.write(f"Total Amount Requested: ${total_amount_requested:.2f}")
        st.write(f"Total Amount Reimbursed: ${total_amount_reimbursed:.2f}")



def get_category_id(category_name):
    query = "SELECT Category_ID FROM Category WHERE Category_Name = %s"

    with conn.cursor() as cursor:
        cursor.execute(query, (category_name,))
        result = cursor.fetchone()

    if result:
        return result[0]  # Assuming Category_ID is the first (and only) column in the result
    else:
        return None  # Return None if the category is not found



# Function to get pending reimbursement requests with additional details including Receipt_Id and Vendor_Name
def get_req_id(employee_id):
    query = """
    SELECT R.Request_Id, C.Category_Name, RD.Receipt_Id, RD.Vendor_Name
    FROM Reimbursement R
    JOIN Category C ON R.Category_Id = C.Category_Id
    LEFT JOIN Reimbursement_Document RD ON R.Request_Id = RD.Request_Id
    WHERE R.Employee_Id = %s AND R.Status_Id = 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (employee_id,))
        result = cursor.fetchall()
    return result


def employee_homepage(employee_id):
   

    # Dropdown for main actions
    action = st.selectbox("Select Action", ["Submit New Reimbursement", "Retract Reimbursement", "Change Current Reimbursement", "Reimbursement History","Approved Reimburesment Details"],index=None,placeholder="Select action")

  
    if action == "Submit New Reimbursement":
        st.header("Submit New Reimbursement")
        category_options = ["Travel", "Meals", "Office Supplies", "Training", "Miscellaneous", "Conference Fees", "Transportation", "Lodging", "Entertainment", "Equipment"]
        category_name = st.selectbox("Select Category", category_options, index=None, placeholder="Select an option")
        category_id = get_category_id(category_name)
        
        if category_id is not None:
            st.write(f"The ID for category '{category_name}' is: {category_id}")
        else:
            st.error(f"Category '{category_name}' not found.")

        amount_requested = st.number_input("Enter Amount Requested", min_value=0.01, step=0.01)
        receipt_id = st.text_input("Enter Receipt ID")
        document_date = st.date_input("Enter Document Date")
        vendor_name = st.text_input("Enter Vendor Name")

        if st.button("Submit Reimbursement"):
            submit_reimbursement(employee_id, category_id, amount_requested, receipt_id, document_date, vendor_name)
            st.success("Reimbursement submitted successfully!")


    elif action == "Retract Reimbursement":
        st.header("Retract Reimbursement")
        st.write("Only pending reimbursement requests can be retracted!")

        pending_requests = get_req_id(employee_id)

        if not pending_requests:
            st.error("No pending reimbursement requests available for this user.")
        else:
            retract_options = st.selectbox(
                "Select Reimbursement to Retract",
                [f"{item[0]} - {item[1]} - Receipt: {item[2]} - Vendor: {item[3]}" for item in pending_requests],
                index=None,
                placeholder="Select an option"
            )
            if retract_options != "None" and st.button("Retract Reimbursement"):
                retract_request_id = int(retract_options.split(" - ")[0])
                retract_reimbursement(retract_request_id)
                st.success("Reimbursement retracted successfully!")

    elif action == "Change Current Reimbursement":
       
        st.header("Change Current Reimbursement")
        st.write("Only pending reimbursement requests can be changed!")

        pending_requests = get_req_id(employee_id)

        if not pending_requests:
            st.error("No pending reimbursement requests available for this user.")
        else:
            change_options = st.selectbox(
                "Select Reimbursement to Change",
                [f"{item[0]} - {item[1]} - Receipt: {item[2]} - Vendor: {item[3]}" for item in pending_requests],
                index=None,
                placeholder="Select an option"
            )
            category_options = ["Travel", "Meals", "Office Supplies", "Training", "Miscellaneous", "Conference Fees", "Transportation", "Lodging", "Entertainment", "Equipment"]
            category_name = st.selectbox("Select Category", category_options, index=None, placeholder="Select an option")
            category_id = get_category_id(category_name)

            if category_id is not None:
                print(f"The ID for category '{category_name}' is: {category_id}")
            else:
                print(f"Category '{category_name}' not found.")

            new_amount = st.number_input("Enter New Amount", min_value=0.01, step=0.01)
            new_receipt_id = st.text_input("Enter New Receipt ID")
            new_document_date = st.date_input("Enter New Document Date")
            new_vendor_name = st.text_input("Enter New Vendor Name")

            if change_options != "None" and st.button("Change Reimbursement"):
                change_request_id = int(change_options.split(" - ")[0])
                change_reimbursement(change_request_id, new_amount, category_id, new_receipt_id, new_document_date, new_vendor_name)
                st.success("Reimbursement changed successfully!")

    elif action == "Reimbursement History":

        st.header("Reimbursement History")
        reimbursement_history, column_names = get_reimbursement_history(employee_id)

        if reimbursement_history:
            df = pd.DataFrame(reimbursement_history, columns=column_names)

            # Rename columns
            df = df.rename(columns={
                "Request_Id": "Request ID",
                "Date_Submitted": "Date Submitted",
                "Category_Name": "Category Name",
                "Amount_Requested": "Amount Requested",
                "Vendor_Name": "Vendor Name",
                "Status": "Status",
                "Receipt_Id": "Receipt ID"
            })

            # Display the dataframe
            st.dataframe(df, height=200)

            # Display the count of pending, approved, and denied requests
            pending_requests = df[df["Status"] == "Pending"]["Request ID"].count()
            approved_requests = df[df["Status"] == "Approved"]["Request ID"].count()
            denied_requests = df[df["Status"].str.startswith("Denied")]["Request ID"].count()

            st.info(f"Pending Requests: {pending_requests}")
            st.success(f"Approved Requests: {approved_requests}")
            st.error(f"Denied Requests: {denied_requests}")
            
        else:
            st.warning("No reimbursement history found.")

    elif action == "Approved Reimburesment Details":
        display_approved_reimbursement_details(employee_id)
        display_approved_reimbursement_details_total(employee_id)

def get_manager_employee_ids(manager_id):
    # Retrieve employee IDs for employees managed by the given manager_id
    query = f"SELECT Employee_Id FROM Employee WHERE Manager_Id = {manager_id};"
    cursor.execute(query)
    results = cursor.fetchall()
    return [str(result[0]) for result in results]

def is_manager(employee_id):
    # Check if the given employee is a manager
    query = f"SELECT COUNT(*) FROM Employee WHERE Manager_Id = {employee_id};"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0] > 0

def get_status_messages():
    # Retrieve status messages from the Status table
    query = "SELECT Status_Message FROM Status;"
    cursor.execute(query)
    results = cursor.fetchall()
    return [result[0] for result in results]

def get_category_names():
    # Retrieve category names from the Category table
    query = "SELECT Category_Name FROM Category;"
    cursor.execute(query)
    results = cursor.fetchall()
    return [result[0] for result in results]

# Streamlit App
st.title("CRMS Employee Portal")
# Ask the user to select either "employee" or "employer"
user_type = st.radio("Select User Type:", ["employee", "employer"])

if user_type == "employer":

    # Ask for employee ID
    employee_id = st.text_input("Enter your Employee ID:")

    # Check if the user entered an ID
    if employee_id:
        # Check if the employee is a manager
        if is_manager(employee_id):
            # Fetch user name from the Employee table using the entered employee ID
            query = f"SELECT First_Name , Last_Name FROM Employee WHERE Employee_Id = {employee_id};"
            cursor.execute(query)
            result = cursor.fetchone()

            # Check if the employee ID is valid
            if result:
                user_name = result[0] + " " + result[1]
                st.success(f"Welcome, {user_name}!")

                # Offer options for the user
                option = st.radio("Select an option:", ["View Reimbursements", "Change Reimbursement Status"])

                if option == "View Reimbursements":
                    # Provide filters
                    selected_employee_id = st.selectbox("Select Employee ID:", ["all"] + [str(eid) for eid in get_manager_employee_ids(employee_id)])
                    selected_status = st.selectbox("Select Status:", ["all"] + get_status_messages())
                    selected_category = st.selectbox("Select Category:", ["all"] + get_category_names())

                    # Construct SQL query based on selected filters
                    query = "SELECT * FROM Reimbursement WHERE "
                    conditions = []

                    if selected_employee_id != "all":
                        conditions.append(f"Employee_Id = {selected_employee_id}")
                    else:
                        # Include all employees managed by the given manager
                        manager_employee_ids = get_manager_employee_ids(employee_id)
                        conditions.append(f"Employee_Id IN ({', '.join(manager_employee_ids)})")

                    if selected_status != "all":
                        status_id_query = f"SELECT Status_Id FROM Status WHERE Status_Message = '{selected_status}';"
                        cursor.execute(status_id_query)
                        status_id = cursor.fetchone()[0]
                        conditions.append(f"Status_Id = {status_id}")

                    if selected_category != "all":
                        category_id_query = f"SELECT Category_Id FROM Category WHERE Category_Name = '{selected_category}';"
                        cursor.execute(category_id_query)
                        category_id = cursor.fetchone()[0]
                        conditions.append(f"Category_Id = {category_id}")

                    if conditions:
                        query += " AND ".join(conditions) + ";"
                        cursor.execute(query)
                        results = cursor.fetchall()

                        # Display filtered results with corresponding category_name and status_message
                        if results:
                            columns = [desc[0] for desc in cursor.description]
                            
                            # Get the index of Category_Id and Status_Id columns
                            category_id_index = columns.index("Category_Id")
                            status_id_index = columns.index("Status_Id")

                            # Replace Category_Id and Status_Id with corresponding names in the DataFrame
                            for i, row in enumerate(results):
                                category_id = row[category_id_index]
                                status_id = row[status_id_index]

                                # Get corresponding category_name
                                category_name_query = f"SELECT Category_Name FROM Category WHERE Category_Id = {category_id};"
                                cursor.execute(category_name_query)
                                category_name = cursor.fetchone()[0]

                                # Get corresponding status_message
                                status_message_query = f"SELECT Status_Message FROM Status WHERE Status_Id = {status_id};"
                                cursor.execute(status_message_query)
                                status_message = cursor.fetchone()[0]

                                # Replace Category_Id and Status_Id with corresponding names
                                results[i] = tuple(list(row[:category_id_index]) + [category_name] + list(row[category_id_index + 1:status_id_index]) + [status_message] + list(row[status_id_index + 1:]))

                            df = pd.DataFrame(results, columns=columns[:category_id_index] + ["Category_Name"] + columns[category_id_index + 1:status_id_index] + ["Status_Message"] + columns[status_id_index + 1:])
                            st.write(df)
                        else:
                            st.warning("No reimbursements found with the selected filters.")


                elif option == "Change Reimbursement Status":
                    manager_employee_ids = get_manager_employee_ids(employee_id)
                    # Display details of pending reimbursement requests submitted by employees managed by the user
                    pending_requests_query = f"SELECT * FROM Reimbursement " \
                                            f"WHERE Employee_Id IN ({', '.join(manager_employee_ids)}) " \
                                            f"AND Status_Id = (SELECT Status_Id FROM Status WHERE Status_Message = 'Pending');"

                    cursor.execute(pending_requests_query)
                    pending_results = cursor.fetchall()
                    print(pending_results)
                    # Display the list of pending reimbursement requests
                    if pending_results:
                        st.write("Pending Reimbursement Requests:")
                        columns = [desc[0] for desc in cursor.description]
                        df_pending = pd.DataFrame(pending_results, columns=columns)
                                    

                        # Get the selected request_id and new status_message from the user
                        selected_request_id = st.selectbox("Select a pending request:", df_pending['Request_Id'].astype(str).tolist())
                        new_status_message = st.selectbox("Select a new status:", ["Pending", "Approved", "Denied-Non-Compliance with Company Policy", "Denied-Lack of Sufficient Documentation", "Denied-Expense Not Business-Related", "Denied-Duplicate Submissions"])

                        # Call the stored procedure to update the reimbursement status
                        update_status_procedure = "CALL UpdateReimbursementStatus(%s, %s);"
                        cursor.execute(update_status_procedure, (selected_request_id, new_status_message))
                        conn.commit()

                        st.success(f"Reimbursement status updated to {new_status_message} for Request ID {selected_request_id}.")

                        # ...

                    else:
                        st.warning("No pending reimbursement requests found for employees you manage.")



            else:
                st.error("Invalid Employee ID. Please enter a valid ID.")

        else:
            st.error("You do not have access.")  #employer doesnt manage any employee
            st.stop()
else:
    employee_id = st.text_input("Enter Employee ID:")

    # Check if the employee ID exists in the database and manager_id is not null
    query_employee = "SELECT COUNT(*) FROM Employee WHERE Employee_Id = %s"
    query_manager = "SELECT COUNT(*) FROM Employee WHERE Employee_Id = %s AND Manager_Id IS NULL"
    
    with conn.cursor() as cursor:
        # Check if the employee exists
        cursor.execute(query_employee, (employee_id,))
        employee_exists = cursor.fetchone()[0] > 0

        # Check if the employee has a manager
        cursor.execute(query_manager, (employee_id,))
        has_manager = cursor.fetchone()[0] > 0

    if not employee_exists:
        st.error("Employee does not exist.")
    elif has_manager:
        st.info("This employee has no higher authorities (Manager Id is NULL).")
    else:
        employee_homepage(employee_id)


# Close the database connection
conn.close()
