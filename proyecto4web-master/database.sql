-- URI Heroku
postgres: // hsihffckvmhbcd : c80bdd334ef7782470866b6d5113e90221b7fecda9d45b18ca042a12d9d81edc @ ec2-174-129-255-128.compute-1.amazonaws.com : 5432 / d20pndefq5jt86


--tabla de usuarios
CREATE TABLE users (
    id SERIAL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    fullname VARCHAR NOT NULL
);

--tabla de libros
CREATE TABLE books (
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);

--tabla de califcaciones
CREATE TABLE reviews (
    isbn VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    opinion VARCHAR NOT NULL,
    rating INTEGER NOT NULL
);
