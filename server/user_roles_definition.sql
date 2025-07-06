CREATE ROLE dbo_rw_role;

CREATE USER python_user
  LOGIN_NAME = 'python_user'
  PASSWORD = '' --actual  password not shown here;
  DEFAULT_ROLE = dbo_rw_role;

GRANT ROLE dbo_rw_role TO USER python_user;

-- Grant usage on database and schema
GRANT USAGE ON DATABASE CHATTY_HOTEL_VOYAGER TO ROLE dbo_rw_role;
GRANT USAGE ON SCHEMA CHATTY_HOTEL_VOYAGER.dbo TO ROLE dbo_rw_role;

-- Grant read-write (SELECT, INSERT, UPDATE, DELETE) on all existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA CHATTY_HOTEL_VOYAGER.dbo TO ROLE dbo_rw_role;

-- Grant read-write on all future tables
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA CHATTY_HOTEL_VOYAGER.dbo TO ROLE dbo_rw_role;

