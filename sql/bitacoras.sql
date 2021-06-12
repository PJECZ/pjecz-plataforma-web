SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

DROP TABLE IF EXISTS bitacoras;
CREATE TABLE bitacoras (
  creado datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modificado datetime DEFAULT CURRENT_TIMESTAMP,
  estatus varchar(1) NOT NULL DEFAULT 'A',
  id int NOT NULL,
  usuario_id int NOT NULL,
  modulo varchar(26) NOT NULL,
  descripcion varchar(256) NOT NULL,
  url varchar(512) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


ALTER TABLE bitacoras
  ADD PRIMARY KEY (id),
  ADD KEY ix_bitacoras_usuario_id (usuario_id),
  ADD KEY ix_bitacoras_modulo (modulo);


ALTER TABLE bitacoras
  MODIFY id int NOT NULL AUTO_INCREMENT;


ALTER TABLE bitacoras
  ADD CONSTRAINT bitacoras_ibfk_1 FOREIGN KEY (usuario_id) REFERENCES usuarios (id);
COMMIT;
