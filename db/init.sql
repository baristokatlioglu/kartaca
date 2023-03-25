create database if not exists kartaca;

GRANT ALL PRIVILEGES ON kartaca.* TO 'kartaca'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;

USE kartaca;

CREATE TABLE country (
CountryID CHAR(2),
CountryName VARCHAR(70)
);

CREATE TABLE currency (
CountryID CHAR(2),
Currency VARCHAR(3)
);
