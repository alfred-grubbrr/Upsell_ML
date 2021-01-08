CREATE TABLE graph_table_company_CompanyID_branch_BranchID_nodes AS (SELECT ItemID FROM Item WHERE companyID = company_id and BranchID = branch_id);

CREATE TABLE graph_table_company_CompanyID_branch_BranchID_edges (
 a INTEGER NOT NULL REFERENCES graph_table_company_CompanyID_branch_BranchID_nodes(id) ON UPDATE CASCADE ON DELETE CASCADE,
 b INTEGER NOT NULL REFERENCES graph_table_company_CompanyID_branch_BranchID_nodes(id) ON UPDATE CASCADE ON DELETE CASCADE,
 PRIMARY KEY (a, b),
 w INTEGER NOT NULL
);