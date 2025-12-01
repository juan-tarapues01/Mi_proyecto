CREATE TABLE IF NOT EXISTS contactos (
      id SERIAL PRIMARY KEY,              
      nombre VARCHAR(100) NOT NULL,       
      correo VARCHAR(100) NOT NULL,       
      mensaje TEXT,                       
      creado TIMESTAMP DEFAULT NOW()  
      
);