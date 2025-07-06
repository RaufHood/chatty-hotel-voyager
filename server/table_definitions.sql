--table definitions in Snowflake:
use database CHATTY_HOTEL_VOYAGER;

create or replace TABLE CHATTY_HOTEL_VOYAGER.DBO.HOTELS (
    HOTEL_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    HOTEL_NAME VARCHAR(255),
    STARS NUMBER(38,0),
    RATING FLOAT,
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    COUNTRY_CODE VARCHAR(5),
    CITY_CODE VARCHAR(5),
    HOTEL_TYPE VARCHAR(50),
    primary key (HOTEL_ID)
);

create or replace TABLE CHATTY_HOTEL_VOYAGER.DBO.TRIPS (
    TRIP_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    USER_ID NUMBER(38,0),
    DATE_START TIMESTAMP_NTZ(9),
    DATE_END TIMESTAMP_NTZ(9),
    TRIP_STATUS VARCHAR(30), --past, in progress, upcoming 
    primary key (TRIP_ID),
    foreign key (USER_ID) references CHATTY_HOTEL_VOYAGER.DBO.USERS(USER_ID)
);

create or replace TABLE CHATTY_HOTEL_VOYAGER.DBO.TRIP_LEGS (
    TRIP_LEG_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    TRIP_ID NUMBER(38,0),
    USER_ID NUMBER(38,0),
    HOTEL_ID NUMBER(38,0),
    ARRIVAL_DATE TIMESTAMP_NTZ(9),
    DEPARTURE_DATE TIMESTAMP_NTZ(9),
    STAY_PRICE FLOAT,
    primary key (TRIP_LEG_ID),
    foreign key (TRIP_ID) references CHATTY_HOTEL_VOYAGER.DBO.TRIPS(TRIP_ID),
    foreign key (USER_ID) references CHATTY_HOTEL_VOYAGER.DBO.USERS(USER_ID),
    foreign key (HOTEL_ID) references CHATTY_HOTEL_VOYAGER.DBO.HOTELS(HOTEL_ID)
);

create or replace TABLE CHATTY_HOTEL_VOYAGER.DBO.USERS (
    USER_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    EMAIL VARCHAR(30),
    NAME VARCHAR(30),
    SURNAME VARCHAR(30),
    PHONE VARCHAR(20),
    AUTO_TOKEN VARCHAR(255), --for Google OAuth
    PWD_HASH CHAR(64), --SHA256 password hash,
    primary key (USER_ID)
);

create or replace TABLE CHATTY_HOTEL_VOYAGER.DBO.CONVERSATION_HEADER (
    COVNERSATION_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    USER_ID NUMBER(38,0),
    TRIP_ID NUMBER(38,0),
    foreign key (USER_ID) references CHATTY_HOTEL_VOYAGER.DBO.USERS(USER_ID),
    foreign key (TRIP_ID) references CHATTY_HOTEL_VOYAGER.DBO.TRIPS(TRIP_ID),
);

create or replace TABLE CHATTY_HOTEL_VOYAGER.DBO.CONVERSATION_CONTENT (
    REPLY_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    CONVERSATION_ID NUMBER(38,0),
    REPLY_TIMESTAMP TIMESTAMP_NTZ(9), --assume GMT +2:00 for simplifity, we can add timezone definition later
    ROLE VARCHAR(10), --user or chatbot
    CONTENT VARCHAR(8000), --should we also add file attatchments?
    foreign key (CONVERSATION_ID) references CONVERSATION_HEADER(CONVERSATION_ID)
);
